# polls/management/commands/seed.py
import random
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role
from polls.models import Poll, PollOption, Vote

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with realistic polling data'
    
    def handle(self, *args, **options):
        self.stdout.write("Deleting old data...")
        models = [Vote, PollOption, Poll, Role]
        
        # Preserve superusers (like admin)
        # User.objects.filter(is_superuser=False).delete()
            
        # Clear all existing data (adjust order if there are foreign key constraints)
        Vote.objects.all().delete()
        PollOption.objects.all().delete()
        Poll.objects.all().delete()
        User.objects.all().delete()  # This must come before Role deletion if Role has FK to User
        Role.objects.all().delete()
        for model in models:
            model.objects.all().delete()
        
        self.stdout.write("Creating roles...")
        roles_data = [
            {'name': 'admin', 'description': 'Administrator role'},
            {'name': 'creator', 'description': 'Content creator role'},
            {'name': 'user', 'description': 'Regular user role'}
        ]
        
        for role_data in roles_data:
            Role.objects.create(**role_data)
            
        admin_role = Role.objects.get(name='admin')
        creator_role = Role.objects.get(name='creator')
        user_role = Role.objects.get(name='user')
        
        self.stdout.write("Creating users...")
        # Create admin
        admin = User.objects.create_superuser(
            username='khalifah',
            email='admin@khalfanathman.dev',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        admin.roles.add(admin_role, creator_role)
        
        # Create creators
        creators = []
        creator_profiles = [
            {'first_name': 'Emma', 'last_name': 'Thompson', 'username': 'emma_creator'},
            {'first_name': 'James', 'last_name': 'Wilson', 'username': 'james_creator'},
            {'first_name': 'Sophia', 'last_name': 'Chen', 'username': 'sophia_creator'},
            {'first_name': 'Michael', 'last_name': 'Rodriguez', 'username': 'michael_creator'},
            {'first_name': 'Olivia', 'last_name': 'Patel', 'username': 'olivia_creator'}
        ]
        
        for profile in creator_profiles:
            user = User.objects.create_user(
                **profile,
                email=f"{profile['username']}@example.com",
                password=f"{profile['username']}123"
            )
            user.roles.add(creator_role)
            creators.append(user)
        
        # Create regular users
        users = []
        for i in range(1, 51):  # 50 regular users
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=f'user{i}123',
                first_name=f'User{i}',
                last_name='Test'
            )
            user.roles.add(user_role)
            users.append(user)
        
        self.stdout.write("Creating polls...")
        poll_templates = [
            {
                "title": "Favorite Programming Language",
                "description": "Which programming language do you enjoy working with the most?",
                "options": ["Python", "JavaScript", "Java", "C#", "Go", "Rust"]
            },
            {
                "title": "Best Web Framework",
                "description": "What's your preferred backend framework?",
                "options": ["Django", "Flask", "Spring Boot", "Express", "ASP.NET Core", "Laravel"]
            },
            {
                "title": "Preferred Cloud Provider",
                "description": "Which cloud platform do you use most?",
                "options": ["AWS", "Azure", "Google Cloud", "DigitalOcean", "Heroku", "Linode"]
            },
            {
                "title": "Favorite Database",
                "description": "Which database technology do you prefer?",
                "options": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra"]
            },
            {
                "title": "Top JavaScript Framework",
                "description": "What's your go-to frontend framework?",
                "options": ["React", "Vue", "Angular", "Svelte", "Next.js", "SolidJS"]
            },
            {
                "title": "Preferred Operating System",
                "description": "Which OS do you use for development?",
                "options": ["Windows", "macOS", "Linux", "BSD"]
            },
            {
                "title": "Most Important Tech Skill",
                "description": "What skill is most valuable for developers?",
                "options": ["Problem Solving", "Algorithms", "System Design", "Communication", "Testing"]
            }
        ]
        
        polls = []
        for template in poll_templates:
            creator = random.choice(creators)
            created_at = timezone.now() - timedelta(days=random.randint(1, 30))
            closes_at = created_at + timedelta(days=random.randint(3, 60))
            
            poll = Poll.objects.create(
                user=creator,
                title=template["title"],
                description=template["description"],
                created_at=created_at,
                closes_at=closes_at,
                status=random.choice(['active', 'active', 'active', 'draft', 'closed'])
            )
            polls.append(poll)
            
            # Create options
            for option_text in template["options"]:
                PollOption.objects.create(
                    poll=poll,
                    text=option_text
                )
        
        self.stdout.write("Creating votes...")
        # Create votes for active and closed polls
        votable_polls = Poll.objects.filter(status__in=['active', 'closed'])
        
        for poll in votable_polls:
            options = list(poll.options.all())
            time_diff = (poll.closes_at - poll.created_at).total_seconds()
    
            # Skip if closes_at is before created_at
            if time_diff <= 0:
                continue
            # Determine number of voters (50-90% of users)
            num_voters = random.randint(
                int(len(users) * 0.5), 
                int(len(users) * 0.9)
            )
            voters = random.sample(users, k=num_voters)
            
            for voter in voters:
                # Each voter votes once per poll
                option = random.choice(options)
                vote_date = poll.created_at + timedelta(
                    seconds=random.randint(0, int((poll.closes_at - poll.created_at).total_seconds()))
                )
                Vote.objects.create(
                    user=voter,
                    option=option,
                    voted_at=vote_date
                )
        
        # Create some draft polls
        for i in range(3):
            creator = random.choice(creators)
            created_at = timezone.now() - timedelta(days=random.randint(1, 30))
            closes_at = created_at + timedelta(days=random.randint(3, 60)) 
            
            poll = Poll.objects.create(
                user=creator,
                title=f"Draft Poll {i+1}",
                description="This is a draft poll that hasn't been published yet",
                created_at=created_at,
                closes_at=closes_at,
                status='draft'
            )
            for j in range(3, 6):
                PollOption.objects.create(
                    poll=poll,
                    text=f"Option {j}"
                )
        
        self.stdout.write(self.style.SUCCESS("Successfully seeded database with:"))
        self.stdout.write(f"- {User.objects.count()} users")
        self.stdout.write(f"- {Role.objects.count()} roles")
        self.stdout.write(f"- {Poll.objects.count()} polls")
        self.stdout.write(f"- {PollOption.objects.count()} poll options")
        self.stdout.write(f"- {Vote.objects.count()} votes")