import json
import os
from src.utils.helpers import clean_markdown_formatting, save_json, get_file_size, get_timestamp, html_to_markdown, format_date_header
from configs.config import ZENDESK_OUTPUT_DIR


def zendesk_transform_tickets() -> str:
    """Transformer les tickets Zendesk pour Chatwoot"""
    date_today = get_timestamp()
    input_file = f"{ZENDESK_OUTPUT_DIR}/clean_export_data/zendesk_tickets_clean_{date_today}.json"
    
    print(f"Transformation tickets: {os.path.basename(input_file)}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tickets = data.get('tickets', [])
    transformed_tickets = []
    
    for ticket in tickets:
        comments = ticket.get('comments', [])
        transformed_comments = []
        
        for comment in comments:
            html_body = comment.get('html_body', '')
            if html_body:
                markdown_content = html_to_markdown(html_body)
            else:
                body = comment.get('body', '')
                markdown_content = body.replace('\n', '<br>')
                if markdown_content:
                    markdown_content = clean_markdown_formatting(markdown_content)
            
            created_at = comment.get('created_at', '')
            date_header = format_date_header(created_at)
            
            if markdown_content:
                final_content = f"{date_header}<br><br>{markdown_content}"
            else:
                final_content = date_header
            
            transformed_comment = {
                'id': comment.get('id'),
                'author_id': comment.get('author_id'),
                'content': final_content,
                'public': comment.get('public'),
                'created_at': comment.get('created_at'),
                'attachments': comment.get('attachments', [])
            }
            transformed_comments.append(transformed_comment)
        
        description = ticket.get('description', '')
        created_at = ticket.get('created_at', '')
        
        if description:
            description_with_br = description.replace('\n', '<br>')
            
            cleaned_description = clean_markdown_formatting(description_with_br)
            
            description_header = format_date_header(created_at)
            transformed_description = f"{description_header}<br><br>{cleaned_description}"
        else:
            transformed_description = ""
        
        transformed_ticket = {
            'id': ticket.get('id'),
            'subject': ticket.get('subject'),
            'description': transformed_description,
            'status': ticket.get('status'),
            'priority': ticket.get('priority'),
            'type': ticket.get('type'),
            'requester_id': ticket.get('requester_id'),
            'assignee_id': ticket.get('assignee_id'),
            'group_id': ticket.get('group_id'),
            'organization_id': ticket.get('organization_id'),
            'created_at': ticket.get('created_at'),
            'updated_at': ticket.get('updated_at'),
            'tags': ticket.get('tags', []),
            'comments': transformed_comments
        }
        transformed_tickets.append(transformed_ticket)
    
    transformed_data = {
        'metadata': {
            'transformed_at': get_timestamp(include_time=True),
            'count': len(transformed_tickets),
            'source': 'zendesk_tickets_cleaned',
            'transformations': ['html_to_markdown', 'date_headers_added', 'newlines_to_br', 'markdown_cleaned']
        },
        'tickets': transformed_tickets
    }
    
    output_dir = f"{ZENDESK_OUTPUT_DIR}/transformed_data"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"zendesk_tickets_transformed_{date_today}.json"
    filepath = os.path.join(output_dir, filename)
    save_json(transformed_data, filepath)
    
    print(f"Tickets transformés: {filename} ({get_file_size(filepath)}) - {len(transformed_tickets)} items")
    return filepath

def test_zendesk_transform():
    """Test de transformation"""
    zendesk_transform_tickets()


if __name__ == "__main__":
    test_zendesk_transform()