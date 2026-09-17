"""
Module 1: Data Extraction
=========================
"""

import re
import hashlib
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse
import ipaddress

@dataclass
class EmailIOC:
    value: str
    ioc_type: str
    source: str
    extracted_at: str

@dataclass
class ExtractedEmail:
    sender: Optional[str]
    receiver: Optional[str]
    date: Optional[str]
    subject: Optional[str]
    body: str
    iocs: List[EmailIOC]
    email_hash: str
    extraction_timestamp: str
    dataset_source: str
    original_label: int
    confidence: float

class URLExtractor:
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]*',
        re.IGNORECASE
    )
    
    @staticmethod
    def extract_urls(text: str) -> Set[str]:
        if not text:
            return set()
        matches = URLExtractor.URL_PATTERN.findall(text)
        valid_urls = set()
        for url in matches:
            if URLExtractor._is_valid_url(url):
                valid_urls.add(url)
        return valid_urls
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

class DomainExtractor:
    @staticmethod
    def extract_domains_from_urls(urls: Set[str]) -> Set[str]:
        domains = set()
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
                domain = domain.split(':')[0]
                if domain:
                    domains.add(domain)
            except:
                continue
        return domains
    
    @staticmethod
    def extract_email_domains(text: str) -> Set[str]:
        email_pattern = re.compile(r'[\w\.-]+@([\w\.-]+)', re.IGNORECASE)
        matches = email_pattern.findall(text)
        return set(matches) if matches else set()

class IPExtractor:
    IPv4_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )
    
    @staticmethod
    def extract_ips(text: str) -> Set[str]:
        if not text:
            return set()
        matches = IPExtractor.IPv4_PATTERN.findall(text)
        valid_ips = set()
        for ip in matches:
            if IPExtractor._is_valid_ip(ip):
                valid_ips.add(ip)
        return valid_ips
    
    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

class DataExtractor:
    @staticmethod
    def extract_email(
        sender: Optional[str],
        receiver: Optional[str],
        date: Optional[str],
        subject: Optional[str],
        body: str,
        dataset_source: str,
        label: int
    ) -> ExtractedEmail:
        import pandas as pd
        sender = None if (sender is None or pd.isna(sender)) else str(sender)
        receiver = None if (receiver is None or pd.isna(receiver)) else str(receiver)
        date = None if (date is None or pd.isna(date)) else str(date)
        subject = None if (subject is None or pd.isna(subject)) else str(subject)
        body = "" if (body is None or pd.isna(body)) else str(body)
        
        urls = URLExtractor.extract_urls(body)
        urls.update(URLExtractor.extract_urls(subject or ""))
        
        domains_from_urls = DomainExtractor.extract_domains_from_urls(urls)
        domains_from_emails = DomainExtractor.extract_email_domains(body)
        domains_from_emails.update(
            DomainExtractor.extract_email_domains(subject or "")
        )
        
        ips = IPExtractor.extract_ips(body)
        ips.update(IPExtractor.extract_ips(subject or ""))
        
        iocs = []
        timestamp = datetime.now().isoformat()
        
        for url in urls:
            iocs.append(EmailIOC(
                value=url,
                ioc_type='url',
                source='body' if url in URLExtractor.extract_urls(body) else 'subject',
                extracted_at=timestamp
            ))
        
        all_domains = domains_from_urls.union(domains_from_emails)
        for domain in all_domains:
            iocs.append(EmailIOC(
                value=domain,
                ioc_type='domain',
                source='extracted_from_url_or_email',
                extracted_at=timestamp
            ))
        
        for ip in ips:
            iocs.append(EmailIOC(
                value=ip,
                ioc_type='ip',
                source='body' if ip in IPExtractor.extract_ips(body) else 'subject',
                extracted_at=timestamp
            ))
        
        body_for_hash = (body or "").encode('utf-8')
        email_hash = hashlib.sha256(body_for_hash).hexdigest()
        
        return ExtractedEmail(
            sender=sender,
            receiver=receiver,
            date=date,
            subject=subject,
            body=body,
            iocs=iocs,
            email_hash=email_hash,
            extraction_timestamp=timestamp,
            dataset_source=dataset_source,
            original_label=label,
            confidence=0.95
        )
