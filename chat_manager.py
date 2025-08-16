#!/usr/bin/env python3
"""
Chat History Manager for RAG Application

This utility helps manage chat histories, including listing, searching, 
exporting, and cleaning up old conversations.
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import csv

CHAT_HISTORY_DIR = "chat_history"

def ensure_chat_dir():
    """Ensure chat history directory exists."""
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
        print(f"Created chat history directory: {CHAT_HISTORY_DIR}")

def list_chats(limit: Optional[int] = None, show_details: bool = False) -> List[Dict]:
    """List all available chats."""
    ensure_chat_dir()
    
    chats = []
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(CHAT_HISTORY_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    
                chat_info = {
                    "id": chat_data.get("id", filename[:-5]),
                    "title": chat_data.get("title", "Untitled Chat"),
                    "created_at": chat_data.get("created_at", ""),
                    "updated_at": chat_data.get("updated_at", ""),
                    "message_count": len(chat_data.get("messages", [])),
                    "file_path": file_path
                }
                
                if show_details:
                    messages = chat_data.get("messages", [])
                    if messages:
                        chat_info["first_message"] = messages[0].get("content", "")[:100] + "..."
                        chat_info["last_message"] = messages[-1].get("content", "")[:100] + "..."
                
                chats.append(chat_info)
                
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error reading {filename}: {e}")
    
    # Sort by updated_at descending
    chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    if limit:
        chats = chats[:limit]
    
    return chats

def search_chats(query: str, limit: Optional[int] = None) -> List[Dict]:
    """Search chats by content or title."""
    ensure_chat_dir()
    
    matching_chats = []
    query_lower = query.lower()
    
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(CHAT_HISTORY_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                # Check title
                title = chat_data.get("title", "").lower()
                if query_lower in title:
                    matching_chats.append({
                        "id": chat_data.get("id", filename[:-5]),
                        "title": chat_data.get("title", "Untitled Chat"),
                        "updated_at": chat_data.get("updated_at", ""),
                        "match_type": "title",
                        "file_path": file_path
                    })
                    continue
                
                # Check message content
                messages = chat_data.get("messages", [])
                for i, message in enumerate(messages):
                    content = message.get("content", "").lower()
                    if query_lower in content:
                        matching_chats.append({
                            "id": chat_data.get("id", filename[:-5]),
                            "title": chat_data.get("title", "Untitled Chat"),
                            "updated_at": chat_data.get("updated_at", ""),
                            "match_type": f"message_{i+1}",
                            "match_content": message.get("content", "")[:200] + "...",
                            "file_path": file_path
                        })
                        break  # Only include each chat once
                        
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error searching {filename}: {e}")
    
    # Sort by updated_at descending
    matching_chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    if limit:
        matching_chats = matching_chats[:limit]
    
    return matching_chats

def export_chat(chat_id: str, format: str = "json") -> bool:
    """Export a specific chat to different formats."""
    ensure_chat_dir()
    
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    if not os.path.exists(file_path):
        print(f"Chat not found: {chat_id}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)
        
        title = chat_data.get("title", "Untitled Chat")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format.lower() == "txt":
            # Export as text
            export_path = f"{safe_title}.txt"
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(f"Chat Title: {title}\n")
                f.write(f"Created: {chat_data.get('created_at', 'Unknown')}\n")
                f.write(f"Updated: {chat_data.get('updated_at', 'Unknown')}\n")
                f.write("=" * 50 + "\n\n")
                
                for message in chat_data.get("messages", []):
                    msg_type = "👤 User" if message.get("type") == "human" else "🤖 Assistant"
                    timestamp = message.get("timestamp", "")
                    content = message.get("content", "")
                    
                    f.write(f"{msg_type} ({timestamp}):\n{content}\n\n")
                    f.write("-" * 30 + "\n\n")
            
            print(f"Exported to: {export_path}")
            
        elif format.lower() == "csv":
            # Export as CSV
            export_path = f"{safe_title}.csv"
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "Content", "Timestamp"])
                
                for message in chat_data.get("messages", []):
                    writer.writerow([
                        message.get("type", ""),
                        message.get("content", ""),
                        message.get("timestamp", "")
                    ])
            
            print(f"Exported to: {export_path}")
            
        else:
            # Export as JSON (default)
            export_path = f"{safe_title}.json"
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            print(f"Exported to: {export_path}")
        
        return True
        
    except Exception as e:
        print(f"Error exporting chat: {e}")
        return False

def cleanup_old_chats(days: int = 30, dry_run: bool = True) -> int:
    """Clean up chats older than specified days."""
    ensure_chat_dir()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(CHAT_HISTORY_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                updated_str = chat_data.get("updated_at", "")
                if updated_str:
                    updated_date = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    updated_date = updated_date.replace(tzinfo=None)  # Remove timezone for comparison
                    
                    if updated_date < cutoff_date:
                        title = chat_data.get("title", "Untitled Chat")
                        if dry_run:
                            print(f"Would delete: {title} (updated: {updated_str})")
                        else:
                            os.remove(file_path)
                            print(f"Deleted: {title}")
                        deleted_count += 1
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    if dry_run and deleted_count > 0:
        print(f"\nDry run: {deleted_count} chat(s) would be deleted.")
        print("Run with --confirm to actually delete them.")
    elif not dry_run:
        print(f"Deleted {deleted_count} old chat(s).")
    
    return deleted_count

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Manage chat history for RAG application")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all chats")
    list_parser.add_argument("--limit", type=int, help="Limit number of results")
    list_parser.add_argument("--details", action="store_true", help="Show additional details")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search chats")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, help="Limit number of results")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export a chat")
    export_parser.add_argument("chat_id", help="Chat ID to export")
    export_parser.add_argument("--format", choices=["json", "txt", "csv"], default="json", help="Export format")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old chats")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Delete chats older than this many days")
    cleanup_parser.add_argument("--confirm", action="store_true", help="Actually delete (not dry run)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        chats = list_chats(args.limit, args.details)
        if not chats:
            print("No chats found.")
        else:
            print(f"Found {len(chats)} chat(s):\n")
            for chat in chats:
                print(f"ID: {chat['id']}")
                print(f"Title: {chat['title']}")
                print(f"Messages: {chat['message_count']}")
                print(f"Updated: {chat['updated_at']}")
                
                if args.details and 'first_message' in chat:
                    print(f"First: {chat['first_message']}")
                    print(f"Last: {chat['last_message']}")
                
                print("-" * 40)
    
    elif args.command == "search":
        results = search_chats(args.query, args.limit)
        if not results:
            print(f"No chats found matching: {args.query}")
        else:
            print(f"Found {len(results)} matching chat(s):\n")
            for result in results:
                print(f"ID: {result['id']}")
                print(f"Title: {result['title']}")
                print(f"Match: {result['match_type']}")
                if 'match_content' in result:
                    print(f"Content: {result['match_content']}")
                print(f"Updated: {result['updated_at']}")
                print("-" * 40)
    
    elif args.command == "export":
        success = export_chat(args.chat_id, args.format)
        if not success:
            exit(1)
    
    elif args.command == "cleanup":
        deleted = cleanup_old_chats(args.days, not args.confirm)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
