from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import User, Notification
from academics.models import Department, Semester, Course, Announcement

class Command(BaseCommand):
    help = 'Seeds UniEnroll database with initial departments, semester, courses, accounts, and announcements.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting UniEnroll demo data seeding..."))

        # 1. Create Active Semester
        semester, created = Semester.objects.get_or_create(
            code='FALL2026',
            defaults={
                'name': 'Fall Semester 2026',
                'is_active': True,
                'max_credits': 18
            }
        )
        if created:
            self.stdout.write(f"  + Created Active Semester: {semester.name}")

        # 2. Create Departments
        depts_data = [
            ('CS', 'Department of Computer Science', 'Core programming, software engineering, and systems.'),
            ('MATH', 'Department of Mathematics', 'Calculus, linear algebra, and discrete mathematics.'),
            ('PHY', 'Department of Physics', 'Classical mechanics, electromagnetism, and quantum physics.'),
            ('AI', 'Department of Artificial Intelligence', 'Machine learning, deep neural networks, and NLP.'),
            ('DS', 'Department of Data Science', 'Big data analytics, statistics, and data engineering.')
        ]

        dept_objs = {}
        for code, name, desc in depts_data:
            dept = Department.objects.filter(code=code).first()
            if not dept:
                dept = Department.objects.create(code=code, name=name, description=desc)
            dept_objs[code] = dept
            self.stdout.write(f"  + Department: {dept.code} - {dept.name}")

        # 3. Create Courses
        courses_data = [
            ('CS101', 'Introduction to Computer Science', 'CS', 4, Decimal('1500.00'), 'Mon / Wed', '09:00 AM - 10:30 AM', 'Tech Hall 101'),
            ('CS202', 'Data Structures & Algorithms', 'CS', 4, Decimal('1800.00'), 'Tue / Thu', '11:00 AM - 12:30 PM', 'Tech Hall 202'),
            ('CS301', 'Database Management Systems', 'CS', 4, Decimal('1800.00'), 'Mon / Wed', '02:00 PM - 03:30 PM', 'Lab B-301'),
            ('MATH101', 'Calculus & Analytical Geometry', 'MATH', 4, Decimal('1200.00'), 'Tue / Thu', '09:00 AM - 10:30 AM', 'Math Annex 12'),
            ('MATH201', 'Linear Algebra & Matrix Theory', 'MATH', 3, Decimal('1200.00'), 'Fri', '09:00 AM - 12:00 PM', 'Math Annex 15'),
            ('PHY101', 'General Physics I: Mechanics', 'PHY', 4, Decimal('1400.00'), 'Mon / Wed', '11:00 AM - 12:30 PM', 'Science Bldg 401'),
            ('AI101', 'Introduction to AI & Neural Networks', 'AI', 4, Decimal('2000.00'), 'Tue / Thu', '02:00 PM - 03:30 PM', 'AI Lab 501'),
            ('DS101', 'Data Analytics with Python & Pandas', 'DS', 4, Decimal('1800.00'), 'Mon / Wed', '04:00 PM - 05:30 PM', 'Lab C-202')
        ]

        for code, title, dcode, credits, fee_cr, days, slot, room in courses_data:
            course = Course.objects.filter(code=code).first()
            if not course:
                course = Course.objects.create(
                    code=code,
                    title=title,
                    department=dept_objs[dcode],
                    credits=credits,
                    fee_per_credit=fee_cr,
                    schedule_days=days,
                    time_slot=slot,
                    room_location=room,
                    max_capacity=60
                )
            self.stdout.write(f"  + Course: {course.code} - {course.title} ({course.credits} Cr)")

        # 4. Create Seed Users
        admin_email = 'admin@dit.edu'
        if not User.objects.filter(email=admin_email).exists():
            admin_user = User.objects.create_superuser(
                email=admin_email,
                password='AdminPassword123!',
                first_name='Dean',
                last_name='Administrator'
            )
            self.stdout.write(f"  + Created Admin Account: {admin_email} (Password: AdminPassword123!)")

        student_email = 'student@dit.edu'
        if not User.objects.filter(email=student_email).exists():
            student_user = User.objects.create_user(
                email=student_email,
                password='StudentPassword123!',
                first_name='Alex',
                last_name='Rivera',
                role=User.Role.STUDENT
            )
            self.stdout.write(f"  + Created Student Account: {student_email} (Password: StudentPassword123!)")

            # Notification for student
            Notification.objects.create(
                user=student_user,
                title='Welcome to UniEnroll Platform!',
                message='Your DIT student portal account is initialized. Browse the course catalog to enroll.',
                notification_type=Notification.Type.GENERAL
            )

        # 5. Create Sample Announcements
        announcements_data = [
            ("Fall 2026 Registration Open", "Semester course registration for Fall 2026 is officially open. Please register before the credit deadline.", Announcement.Category.GENERAL),
            ("Digital Library Access Granted", "All registered students now have full access to IEEE and ACM digital research papers.", Announcement.Category.GENERAL),
            ("Semester Fee Payment Guidelines", "Semester fee checkout is processed securely via Razorpay payment gateway.", Announcement.Category.FEES)
        ]

        for title, content, cat in announcements_data:
            if not Announcement.objects.filter(title=title).exists():
                Announcement.objects.create(
                    title=title,
                    content=content,
                    category=cat
                )
                self.stdout.write(f"  + Announcement: {title}")

        self.stdout.write(self.style.SUCCESS("UniEnroll demo data seeding completed successfully!"))
