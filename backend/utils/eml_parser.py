"""
EML File Parser
===============
Handles .eml files (raw email format from Outlook, Gmail, etc.)
"""

import email
from email.parser import BytesParser
from email.policy import default
from typing import Optional, Tuple

class EMLParser:
    """Parse .eml files and extract email components"""
    
    @staticmethod
    def parse_eml_file(filepath: str) -> dict:
        """
        Parse an .eml file and return email components
        """
        try:
            with open(filepath, 'rb') as f:
                msg = BytesParser(policy=default).parse(f)
            
            return EMLParser._extract_email_parts(msg)
        
        except Exception as e:
            raise Exception(f"Error parsing EML file: {e}")
    
    @staticmethod
    def parse_eml_string(eml_content: str) -> dict:
        """Parse EML content from string"""
        try:
            msg = email.message_from_string(eml_content)
            return EMLParser._extract_email_parts(msg)
        
        except Exception as e:
            raise Exception(f"Error parsing EML string: {e}")
    
    @staticmethod
    def _extract_email_parts(msg) -> dict:
        """Extract all parts from email message"""
        
        sender = msg.get('From', None)
        receiver = msg.get('To', None)
        date = msg.get('Date', None)
        subject = msg.get('Subject', None)
        
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                        break
                
                elif content_type == 'text/html' and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload()
        
        spf_result = msg.get('Received-SPF', None)
        dkim_result = msg.get('DKIM-Signature', None)
        dmarc_result = msg.get('DMARC-Result', None)
        
        return {
            'sender': sender,
            'receiver': receiver,
            'date': date,
            'subject': subject,
            'body': body,
            'spf_result': spf_result,
            'dkim_result': dkim_result,
            'dmarc_result': dmarc_result,
            'is_multipart': msg.is_multipart()
        }
