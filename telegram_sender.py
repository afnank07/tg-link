import asyncio
import sys
import argparse
import logging
from typing import List, Optional
from telethon import TelegramClient, errors
from telethon.tl.types import User
from config import TelegramConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_sender.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramSender:
    """Main class for sending Telegram messages using the Client API."""
    
    def __init__(self):
        """Initialize the Telegram sender with configuration."""
        try:
            self.config = TelegramConfig()
            self.client = TelegramClient(
                self.config.get_session_name(),
                self.config.get_api_id(),
                self.config.get_api_hash()
            )
        except Exception as e:
            logger.error(f"Failed to initialize TelegramSender: {e}")
            raise
    
    async def connect(self):
        """Connect to Telegram and authenticate if necessary."""
        try:
            await self.client.start(phone=self.config.get_phone_number())
            logger.info("Successfully connected to Telegram")
            
            # Get information about the authenticated user
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'no username'})")
            
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Telegram."""
        await self.client.disconnect()
        logger.info("Disconnected from Telegram")
    
    async def resolve_username(self, username: str) -> Optional[User]:
        """
        Resolve a username to a Telegram user.
        
        Args:
            username: The username to resolve (with or without @)
        
        Returns:
            User object if found, None otherwise
        """
        # Remove @ if present
        clean_username = username.lstrip('@')
        
        try:
            entity = await self.client.get_entity(clean_username)
            if isinstance(entity, User):
                return entity
            else:
                logger.warning(f"@{clean_username} is not a user (might be a channel or group)")
                return None
        except errors.UsernameNotOccupiedError:
            logger.error(f"Username @{clean_username} not found")
            return None
        except errors.UsernameInvalidError:
            logger.error(f"Username @{clean_username} is invalid")
            return None
        except Exception as e:
            logger.error(f"Error resolving username @{clean_username}: {e}")
            return None
    
    async def send_message(self, username: str, message: str) -> bool:
        """
        Send a message to a specific username.
        
        Args:
            username: The username to send to (with or without @)
            message: The message to send
        
        Returns:
            True if successful, False otherwise
        """
        user = await self.resolve_username(username)
        if not user:
            return False
        
        try:
            await self.client.send_message(user, message)
            logger.info(f"Message sent successfully to @{username}")
            return True
        except errors.FloodWaitError as e:
            logger.error(f"Rate limited. Need to wait {e.seconds} seconds")
            return False
        except errors.PeerFloodError:
            logger.error("Too many requests. Please try again later")
            return False
        except Exception as e:
            logger.error(f"Failed to send message to @{username}: {e}")
            return False
    
    async def send_bulk_messages(self, usernames: List[str], message: str, delay: int = 1) -> dict:
        """
        Send the same message to multiple usernames.
        
        Args:
            usernames: List of usernames to send to
            message: The message to send
            delay: Delay between messages in seconds (to avoid rate limiting)
        
        Returns:
            Dictionary with success/failure counts and details
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(usernames)
        }
        
        for username in usernames:
            success = await self.send_message(username, message)
            if success:
                results['successful'].append(username)
            else:
                results['failed'].append(username)
            
            # Add delay to avoid rate limiting
            if delay > 0:
                await asyncio.sleep(delay)
        
        logger.info(f"Bulk messaging complete: {len(results['successful'])}/{results['total']} successful")
        return results
    
    async def interactive_mode(self):
        """Interactive mode for sending messages."""
        print("\n=== Telegram Message Sender - Interactive Mode ===")
        print("Type 'quit' or 'exit' to stop")
        
        while True:
            try:
                username = input("\nEnter username (with or without @): ").strip()
                if username.lower() in ['quit', 'exit']:
                    break
                
                if not username:
                    print("Please enter a valid username")
                    continue
                
                message = input("Enter message: ").strip()
                if not message:
                    print("Please enter a message")
                    continue
                
                print(f"Sending message to @{username.lstrip('@')}...")
                success = await self.send_message(username, message)
                
                if success:
                    print("✅ Message sent successfully!")
                else:
                    print("❌ Failed to send message")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

async def main():
    """Main function to handle command line arguments and run the appropriate mode."""
    parser = argparse.ArgumentParser(description='Send Telegram messages using your personal account')
    parser.add_argument('username', nargs='?', help='Username to send message to (with or without @)')
    parser.add_argument('message', nargs='?', help='Message to send')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--bulk', '-b', help='File containing usernames (one per line)')
    parser.add_argument('--delay', '-d', type=int, default=1, help='Delay between bulk messages (seconds)')
    
    args = parser.parse_args()
    
    # Initialize sender
    try:
        sender = TelegramSender()
        await sender.connect()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        return 1
    
    try:
        if args.interactive:
            # Interactive mode
            await sender.interactive_mode()
        
        elif args.bulk:
            # Bulk messaging mode
            if not args.message:
                print("Error: Message is required for bulk messaging")
                return 1
            
            try:
                with open(args.bulk, 'r') as f:
                    usernames = [line.strip() for line in f if line.strip()]
                
                if not usernames:
                    print("Error: No usernames found in file")
                    return 1
                
                print(f"Sending message to {len(usernames)} users...")
                results = await sender.send_bulk_messages(usernames, args.message, args.delay)
                
                print(f"\nResults:")
                print(f"✅ Successful: {len(results['successful'])}")
                print(f"❌ Failed: {len(results['failed'])}")
                
                if results['failed']:
                    print(f"Failed usernames: {', '.join(results['failed'])}")
                
            except FileNotFoundError:
                print(f"Error: File '{args.bulk}' not found")
                return 1
        
        elif args.username and args.message:
            # Single message mode
            print(f"Sending message to @{args.username.lstrip('@')}...")
            success = await sender.send_message(args.username, args.message)
            
            if success:
                print("✅ Message sent successfully!")
            else:
                print("❌ Failed to send message")
                return 1
        
        else:
            # No valid arguments, show help
            parser.print_help()
            return 1
    
    finally:
        await sender.disconnect()
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
