"""
Pub/Sub Manager for agent-to-agent communication
Handles message publishing, subscribing, and dead letter queue management
"""

import os
import json
import time
from typing import Dict, Any, Callable, Optional
from google.cloud import pubsub_v1
from google.api_core import retry
from concurrent.futures import TimeoutError
from src.monitoring.logger import StructuredLogger


class PubSubManager:
    """Manages Pub/Sub messaging for agent communication"""
    
    def __init__(self):
        """Initialize Pub/Sub manager"""
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
        
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.logger = StructuredLogger(name='pubsub')
        
        # Topic configuration
        self.topics = {
            'research-complete': f'projects/{self.project_id}/topics/research-complete',
            'content-generated': f'projects/{self.project_id}/topics/content-generated',
            'editing-complete': f'projects/{self.project_id}/topics/editing-complete',
            'seo-optimized': f'projects/{self.project_id}/topics/seo-optimized',
            'task-failed': f'projects/{self.project_id}/topics/task-failed',
            'dlq': f'projects/{self.project_id}/topics/dlq'
        }
        
        # Subscription configuration
        self.subscriptions = {
            'research-complete-sub': f'projects/{self.project_id}/subscriptions/research-complete-sub',
            'content-generated-sub': f'projects/{self.project_id}/subscriptions/content-generated-sub',
            'editing-complete-sub': f'projects/{self.project_id}/subscriptions/editing-complete-sub',
            'seo-optimized-sub': f'projects/{self.project_id}/subscriptions/seo-optimized-sub',
            'task-failed-sub': f'projects/{self.project_id}/subscriptions/task-failed-sub',
            'dlq-sub': f'projects/{self.project_id}/subscriptions/dlq-sub'
        }
    
    def publish_message(
        self,
        topic_name: str,
        message_data: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publish a message to a topic
        
        Args:
            topic_name: Name of the topic (e.g., 'research-complete')
            message_data: Message payload as dictionary
            attributes: Optional message attributes
            
        Returns:
            Message ID
        """
        if topic_name not in self.topics:
            raise ValueError(f"Unknown topic: {topic_name}")
        
        topic_path = self.topics[topic_name]
        
        # Add metadata
        message_data['timestamp'] = time.time()
        message_data['topic'] = topic_name
        
        # Serialize message
        message_bytes = json.dumps(message_data).encode('utf-8')
        
        # Set attributes
        if attributes is None:
            attributes = {}
        
        attributes.update({
            'message_type': topic_name,
            'project_id': message_data.get('project_id', 'unknown'),
            'correlation_id': message_data.get('correlation_id', str(time.time()))
        })
        
        try:
            # Publish with retry
            future = self.publisher.publish(
                topic_path,
                message_bytes,
                **attributes
            )
            
            message_id = future.result(timeout=10)
            
            self.logger.info(
                f"Published message to {topic_name}",
                message_id=message_id,
                topic=topic_name,
                project_id=message_data.get('project_id')
            )
            
            return message_id
            
        except Exception as e:
            self.logger.error(
                f"Failed to publish message to {topic_name}",
                error=str(e),
                topic=topic_name
            )
            raise
    
    def subscribe(
        self,
        subscription_name: str,
        callback: Callable[[pubsub_v1.subscriber.message.Message], None],
        max_messages: int = 10,
        ack_deadline: int = 600
    ) -> pubsub_v1.subscriber.futures.StreamingPullFuture:
        """
        Subscribe to a topic and process messages
        
        Args:
            subscription_name: Name of subscription
            callback: Callback function to process messages
            max_messages: Max messages to process concurrently
            ack_deadline: Acknowledgement deadline in seconds
            
        Returns:
            Streaming pull future
        """
        if subscription_name not in self.subscriptions:
            raise ValueError(f"Unknown subscription: {subscription_name}")
        
        subscription_path = self.subscriptions[subscription_name]
        
        # Configure flow control
        flow_control = pubsub_v1.types.FlowControl(
            max_messages=max_messages,
            max_bytes=10 * 1024 * 1024  # 10MB
        )
        
        # Wrap callback with error handling
        def wrapped_callback(message: pubsub_v1.subscriber.message.Message):
            try:
                self.logger.info(
                    f"Received message from {subscription_name}",
                    message_id=message.message_id,
                    subscription=subscription_name
                )
                
                callback(message)
                message.ack()
                
                self.logger.info(
                    f"Successfully processed message",
                    message_id=message.message_id
                )
                
            except Exception as e:
                self.logger.error(
                    f"Error processing message",
                    error=str(e),
                    message_id=message.message_id,
                    subscription=subscription_name
                )
                
                # Check retry count
                delivery_attempt = int(message.attributes.get('googclient_deliveryattempt', 1))
                
                if delivery_attempt >= 3:
                    # Send to DLQ
                    self._send_to_dlq(message, str(e))
                    message.ack()
                else:
                    # Nack to retry
                    message.nack()
        
        # Start subscriber
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=wrapped_callback,
            flow_control=flow_control
        )
        
        self.logger.info(
            f"Listening for messages on {subscription_name}",
            subscription=subscription_name
        )
        
        return streaming_pull_future
    
    def _send_to_dlq(self, message: pubsub_v1.subscriber.message.Message, error: str):
        """
        Send failed message to dead letter queue
        
        Args:
            message: Original message
            error: Error description
        """
        try:
            dlq_data = {
                'original_message_id': message.message_id,
                'original_data': message.data.decode('utf-8'),
                'original_attributes': dict(message.attributes),
                'error': error,
                'delivery_attempts': int(message.attributes.get('googclient_deliveryattempt', 1)),
                'failed_at': time.time()
            }
            
            self.publish_message('dlq', dlq_data)
            
            self.logger.warning(
                "Message sent to DLQ",
                message_id=message.message_id,
                error=error
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to send message to DLQ",
                error=str(e),
                message_id=message.message_id
            )
    
    def create_topic(self, topic_name: str) -> str:
        """
        Create a new topic if it doesn't exist
        
        Args:
            topic_name: Topic name
            
        Returns:
            Topic path
        """
        topic_path = f'projects/{self.project_id}/topics/{topic_name}'
        
        try:
            topic = self.publisher.create_topic(request={"name": topic_path})
            self.logger.info(f"Created topic: {topic_name}", topic=topic_name)
            return topic.name
        except Exception as e:
            error_str = str(e)
            # Check for both "ALREADY_EXISTS" and "already exists" in various cases
            if "ALREADY_EXISTS" in error_str or "already exists" in error_str or "409" in error_str:
                self.logger.info(f"Topic already exists: {topic_name}", topic=topic_name)
                return topic_path
            else:
                self.logger.error(f"Failed to create topic", error=error_str, topic=topic_name)
                raise
    
    def create_subscription(
        self,
        subscription_name: str,
        topic_name: str,
        ack_deadline_seconds: int = 600,
        enable_dlq: bool = True
    ) -> str:
        """
        Create a new subscription if it doesn't exist
        
        Args:
            subscription_name: Subscription name
            topic_name: Topic to subscribe to
            ack_deadline_seconds: Acknowledgement deadline
            enable_dlq: Enable dead letter queue
            
        Returns:
            Subscription path
        """
        topic_path = f'projects/{self.project_id}/topics/{topic_name}'
        subscription_path = f'projects/{self.project_id}/subscriptions/{subscription_name}'
        
        request = {
            "name": subscription_path,
            "topic": topic_path,
            "ack_deadline_seconds": ack_deadline_seconds,
            "retry_policy": {
                "minimum_backoff": {"seconds": 10},
                "maximum_backoff": {"seconds": 600}
            }
        }
        
        # Configure DLQ
        if enable_dlq:
            dlq_topic_path = self.topics['dlq']
            request["dead_letter_policy"] = {
                "dead_letter_topic": dlq_topic_path,
                "max_delivery_attempts": 5
            }
        
        try:
            subscription = self.subscriber.create_subscription(request=request)
            self.logger.info(
                f"Created subscription: {subscription_name}",
                subscription=subscription_name,
                topic=topic_name
            )
            return subscription.name
        except Exception as e:
            error_str = str(e)
            # Check for both "ALREADY_EXISTS" and "already exists" in various cases
            if "ALREADY_EXISTS" in error_str or "already exists" in error_str or "409" in error_str:
                self.logger.info(
                    f"Subscription already exists: {subscription_name}",
                    subscription=subscription_name
                )
                return subscription_path
            else:
                self.logger.error(
                    f"Failed to create subscription",
                    error=str(e),
                    subscription=subscription_name
                )
                raise
    
    def setup_infrastructure(self):
        """Create all required topics and subscriptions"""
        self.logger.info("Setting up Pub/Sub infrastructure")
        
        # Create DLQ topic first (needed by other subscriptions)
        self.logger.info("Creating DLQ topic first...")
        self.create_topic('dlq')
        
        # Create remaining topics
        for topic_name in ['research-complete', 'content-generated', 'editing-complete', 
                          'seo-optimized', 'task-failed']:
            self.create_topic(topic_name)
        
        # Create DLQ subscription (without its own DLQ)
        self.logger.info("Creating DLQ subscription...")
        self.create_subscription('dlq-sub', 'dlq', enable_dlq=False)
        
        # Create all other subscriptions (with DLQ enabled)
        subscriptions = [
            ('research-complete-sub', 'research-complete'),
            ('content-generated-sub', 'content-generated'),
            ('editing-complete-sub', 'editing-complete'),
            ('seo-optimized-sub', 'seo-optimized'),
            ('task-failed-sub', 'task-failed')
        ]
        
        for sub_name, topic_name in subscriptions:
            self.create_subscription(sub_name, topic_name, enable_dlq=True)
        
        self.logger.info("Pub/Sub infrastructure setup complete")
