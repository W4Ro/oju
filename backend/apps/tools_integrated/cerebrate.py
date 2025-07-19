import requests
import json
from typing import Any, Dict, Optional, List, Set, Tuple
from urllib.parse import urlparse
import re
from django.db import transaction
import uuid
from apps.focal_points.models import FocalFunction, FocalPoint
from apps.entities.models import Domain, Entity, EntityFocalPoint, Platform
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from core.common_function import str_exception
from apps.logsFonc.utils import create_system_log
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CerebrateAPI:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.cerebrate_tags = {}
        self.cerebrate_individuals = {}
        self.cerebrate_organisations = {}
        self.default_function = None
        self.sync_timestamp = datetime.now().isoformat()
        # Dictionnary to map Cerebrate IDs to local IDs
        self.tag_uuid_map = {}
        self.individual_uuid_map = {}
        self.org_uuid_map = {}
        # IDs of synced individuals and organisations
        self.synced_individuals = set()
        self.synced_organisations = set()

    def check_connection(self):
        """Checks if the Cerebrate API is reachable and the login is successful."""
        try:
            response = requests.get(f"{self.base_url}/users", headers=self.headers)
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            logger.error(f"Cerebrate connection error: {str_exception(e)}")
            return False

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Clean and format a phone number."""
        if not phone or not isinstance(phone, str):
            return ""
 
        phone = re.sub(r'[^\d+]', '', phone.strip())
        if not phone.startswith('+'):
            phone = '+' + phone
        if len(phone) <= 1:
            return ""
        return phone

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if the URL is valid."""
        try:
            url = url.replace(' ', '')
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if the email is valid."""
        if not email or not isinstance(email, str):
            return False
        email = email.strip().rstrip(',')
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, email):
            return False
        return True

    @staticmethod
    def extract_urls(url_data: Any) -> List[str]:
        """Extract URLs from a string or list of strings."""
        urls = set()
        if isinstance(url_data, str):
            urls.add(url_data.strip())
        elif isinstance(url_data, list):
            urls.update(u.strip() for u in url_data if isinstance(u, str))
        return [url for url in list(urls) if url]  # Filtrer les chaînes vides

    def get_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Retreive data from Cerebrate API."""
        try:
            for attempt in range(3):
                try:
                    response = requests.get(
                        f"{self.base_url}/{endpoint}",
                        headers=self.headers,
                        timeout=(5, 20)
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.Timeout:
                    if attempt == 2:
                        raise
                    continue
        except Exception as e:
            logger.error(f"Error retrieving data ({endpoint}): {str_exception(e)}")
            return None

    def handle_deleted_items(self, stats: Dict[str, Any]) -> None:
        """
        Handle the deactivation of focal points that are not present in Cerebrate.
        """
        cerebrate_emails = {ind.get('email', '').lower().strip() 
                         for ind in self.cerebrate_individuals 
                         if ind.get('email')}
        
        # Mark focal points as inactive if they are not in Cerebrate
        inactive_count = 0
        if cerebrate_emails:
            inactive_focal_points = FocalPoint.objects.filter(
                is_active=True
            ).exclude(
                email__in=cerebrate_emails
            )
            
            count = inactive_focal_points.count()
            if count > 0:
                inactive_focal_points.update(is_active=False)
                inactive_count = count
                stats['focal_points_deactivated'] = count

    def sync_from_cerebrate(self) -> Dict[str, Any]:
        """
        Synchronise data from Cerebrate to the local database.
        Returns a dictionary with statistics about the synchronization.
        """
        stats = {
            'functions_created': 0,
            'functions_updated': 0,
            'focal_points_created': 0,
            'focal_points_updated': 0,
            'focal_points_unchanged': 0,
            'focal_points_deactivated': 0,
            'entities_created': 0,
            'entities_updated': 0,
            'entities_unchanged': 0,
            'platforms_created': 0,
            'domains_created': 0,
            'logs': []
        }

        # Retrieving data from Cerebrate
        self.cerebrate_tags = self.get_data("tags") or []
        self.cerebrate_individuals = self.get_data("individuals") or []
        self.cerebrate_organisations = self.get_data("organisations") or []
        
        # check if we have the necessary data
        if not all([self.cerebrate_individuals, self.cerebrate_organisations, self.cerebrate_tags]):
            error_msg = "Synchronisation from Cerebrate aborted: unable to fetch resources from cerebrate"
            logger.error(error_msg)
            stats['logs'].append(error_msg)
            return stats

        try:
            self.default_function = FocalFunction.objects.get(name="Default").id
        except FocalFunction.DoesNotExist:
            error_msg = "The default function does not exist. Please run the init_focal_function command."
            logger.error(error_msg)
            stats['logs'].append(error_msg)
            return stats

        try:
            with transaction.atomic():
                # Synchronise tags/focal functions
                self._sync_tags(stats)
                
                # Synchronise individuals/focal points
                self._sync_individuals(stats)
                
                # Synchronise entities/organisations
                self._sync_organisations(stats)
                
                # Handle deactivation of focal points not present in Cerebrate
                self.handle_deleted_items(stats)
                
        except Exception as e:
            error_msg = f"General error while synchronizing: {str_exception(e)}"
            logger.critical(error_msg)
            stats['logs'].append(error_msg)
            raise
        
        logger.info(f"Cerebrate synchronization completed: {stats}")
        return stats

    def _sync_tags(self, stats: Dict[str, Any]) -> None:
        """Synchronise cerebrate tags with local focal functions."""
        for tag in self.cerebrate_tags:
            try:
                if not tag.get('name'):
                    continue
                    
                tag_name = tag['name'].strip()
                focal_function, created = FocalFunction.objects.get_or_create(
                    name=tag_name
                )
                self.tag_uuid_map[tag['id']] = focal_function.id
                
                if created:
                    stats['functions_created'] += 1
                else:
                    stats['functions_updated'] += 1
            except Exception as e:
                error_msg = f"Error creating function {tag.get('name', 'Unknown')}: {str_exception(e)}"
                stats['logs'].append(error_msg)
                logger.warning(error_msg)

    def _sync_individuals(self, stats: Dict[str, Any]) -> None:
        """Synchronise individuals from Cerebrate with local focal points."""
        for individual in self.cerebrate_individuals:
            try:
                # email validation
                if not individual.get('email') or not self.is_valid_email(individual['email']):
                    error_msg = f"Invalid email for {individual.get('full_name', 'Unknown')}: {individual.get('email', '')}"
                    stats['logs'].append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # name validation
                if not individual.get('full_name'):
                    error_msg = f"Missing name for {individual.get('email', 'Unknown')}"
                    stats['logs'].append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # data cleaning
                email = individual['email'].strip()
                full_name = individual['full_name'].strip()
                phone_numbers = self._extract_phone_numbers(individual)
                function_id = self._determine_function_id(individual)
                
                # Create or update focal point
                try:
                    focal_point, created = FocalPoint.objects.get_or_create(
                        email=email,
                        defaults={
                            'full_name': full_name,
                            'phone_number': phone_numbers,
                            'is_active': True,
                            'function_id': function_id
                        }
                    )
                    
                    if created:
                        stats['focal_points_created'] += 1
                        logger.debug(f"Created focal point: {email}")
                    else:
                        # check if we need to update the focal point
                        modified = False
                        if focal_point.full_name != full_name:
                            focal_point.full_name = full_name
                            modified = True
                        
                        if focal_point.phone_number != phone_numbers:
                            focal_point.phone_number = phone_numbers
                            modified = True
                            
                        if focal_point.function_id != function_id:
                            focal_point.function_id = function_id
                            modified = True
                            
                        if not focal_point.is_active:
                            focal_point.is_active = True
                            modified = True
                        
                        if modified:
                            focal_point.save()
                            stats['focal_points_updated'] += 1
                            logger.debug(f"Updated focal point: {email}")
                        else:
                            stats['focal_points_unchanged'] += 1
                            logger.debug(f"Focal point unchanged: {email}")
                    
                    # Mapp id of the individual to the focal point
                    self.individual_uuid_map[individual['id']] = focal_point.id
                    
                except ValidationError as e:
                    error_msg = f"Validation error for {full_name}: {str_exception(e)}"
                    stats['logs'].append(error_msg)
                    logger.warning(error_msg)
                    
            except Exception as e:
                error_msg = f"Error processing individual {individual.get('full_name', 'Unknown')}: {str_exception(e)}"
                stats['logs'].append(error_msg)
                logger.error(error_msg)

    def _extract_phone_numbers(self, individual: Dict[str, Any]) -> List[str]:
        """Extract and clean phone numbers from an individual."""
        phone_numbers = []
        meta_fields = individual.get('meta_fields', {})
        
        if isinstance(meta_fields, dict) and meta_fields.get('CerberusI', {}).get('Mobile Phone'):
            phone_data = meta_fields['CerberusI']['Mobile Phone']
            
            if isinstance(phone_data, str):
                cleaned = self.clean_phone_number(phone_data)
                if cleaned:
                    phone_numbers = [cleaned]
            elif isinstance(phone_data, list):
                phone_numbers = [
                    num for p in phone_data 
                    if p and isinstance(p, str) and (num := self.clean_phone_number(p))
                ]
        return phone_numbers

    def _determine_function_id(self, individual: Dict[str, Any]) -> int:
        """Determine the function ID for an individual based on tags."""
        function_id = self.default_function
        
        if individual.get('tags') and isinstance(individual['tags'], list) and individual['tags']:
            tag_id = individual['tags'][0].get('id')
            if tag_id and tag_id in self.tag_uuid_map:
                function_id = self.tag_uuid_map[tag_id]
        
        return function_id

    def _sync_organisations(self, stats: Dict[str, Any]) -> None:
        """Synchronise organisations from Cerebrate with local entities."""
        for org in self.cerebrate_organisations:
            try:
                # name validation
                if not org.get('name'):
                    error_msg = "Organisation without name, skipping"
                    stats['logs'].append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                org_name = org['name'].strip()
                org_description = org.get('sector', '').strip()
                
                # Create or update the entity
                entity, created = Entity.objects.get_or_create(
                    name=org_name,
                    defaults={
                        'description': org_description
                    }
                )
                
                # update the entity if it already exists
                modified = False
                if not created:
                    if entity.description != org_description:
                        entity.description = org_description
                        modified = True
                        
                    if modified:
                        entity.save()
                        stats['entities_updated'] += 1
                    else:
                        stats['entities_unchanged'] += 1
                else:
                    stats['entities_created'] += 1
                
                # Synchronise urls and platforms
                self._sync_entity_urls(org, entity, stats)
                
                self._sync_entity_alignments(org, entity, stats)
                
            except Exception as e:
                error_msg = f"Entity processing error {org.get('name', 'Unknown')}: {str_exception(e)}"
                stats['logs'].append(error_msg)
                logger.error(error_msg)

    def _sync_entity_urls(self, org: Dict[str, Any], entity: Entity, stats: Dict[str, Any]) -> None:
        """Synchronise urls and platforms for an organisation."""
        urls = set()
        
        if org.get('url'):
            urls.update(self.extract_urls(org['url']))
        
        meta_fields = org.get('meta_fields', {})
        if isinstance(meta_fields, dict):
            cerberus_data = meta_fields.get('Cerberus', {})
            if isinstance(cerberus_data, dict) and cerberus_data.get('URL'):
                urls.update(self.extract_urls(cerberus_data['URL']))
        
        for url in urls:
            if not url or not self.is_valid_url(url):
                stats['logs'].append(f"Invalid URL ignored for {org['name']}: {url}")
                logger.warning(f"Invalid URL ignored for {org['name']}: {url}")
                continue
            
            try:
                parsed_url = urlparse(url)
                domain_name = parsed_url.netloc
                
                domain, domain_created = Domain.objects.get_or_create(
                    name=domain_name
                )
                if domain_created:
                    stats['domains_created'] += 1
                
                platform, platform_created = Platform.objects.get_or_create(
                    url=url,
                    defaults={
                        'entity': entity,
                        'domain': domain,
                        'is_active': True
                    }
                )
                
                if not platform_created:
                    modified = False
                    if platform.entity != entity:
                        platform.entity = entity
                        modified = True
                    
                    if platform.domain != domain:
                        platform.domain = domain
                        modified = True
                        
                    if not platform.is_active:
                        platform.is_active = True
                        modified = True
                        
                    if modified:
                        platform.save()
                
                if platform_created:
                    stats['platforms_created'] += 1
                    
            except Exception as e:
                error_msg = f"Platform creation error {url}: {str_exception(e)}"
                stats['logs'].append(error_msg)
                logger.error(error_msg)

    def _sync_entity_alignments(self, org: Dict[str, Any], entity: Entity, stats: Dict[str, Any]) -> None:
        """Synchronise relationships between organisations and focal points."""
        alignments = org.get('alignments')
        if not isinstance(alignments, dict) or not alignments.get('individual'):
            return
            
        existing_fp_ids = set(
            EntityFocalPoint.objects.filter(entity=entity).values_list('focal_point_id', flat=True)
        )
        
        new_alignments = []
        
        for aligned_individual in alignments['individual']:
            focal_point_id = self.individual_uuid_map.get(aligned_individual['id'])
            if focal_point_id:
                if focal_point_id not in existing_fp_ids:
                    new_alignments.append(
                        EntityFocalPoint(entity=entity, focal_point_id=focal_point_id)
                    )
                existing_fp_ids.discard(focal_point_id)
            else:
                stats['logs'].append(
                    f"Focal point {aligned_individual.get('email', 'Unknown')} not found for entity {org['name']}"
                )
                logger.warning(
                    f"Point focal {aligned_individual.get('email', 'Unknown')} "
                    f"not found for entity {org['name']}"
                )
        
        if new_alignments:
            EntityFocalPoint.objects.bulk_create(new_alignments)
            
        # Option: delete alignments that are no longer present in Cerebrate
        # EntityFocalPoint.objects.filter(entity=entity, focal_point_id__in=existing_fp_ids).delete()