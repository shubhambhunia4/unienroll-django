from django.core.management.base import BaseCommand
from academics.models import Department, Semester, Course
from accounts.models import User
from enrollment.models import Enrollment, EnrollmentItem
from fees.models import SemesterFee

class Command(BaseCommand):
    help = 'Seeds 15 initial courses and default enrolled courses for DIT UniEnroll'

    def handle(self, *args, **options):
        self.stdout.write("Seeding academic data...")

        # Active Semester
        semester, created = Semester.objects.get_or_create(
            code='FALL2026',
            defaults={'name': 'Fall 2026 Semester', 'is_active': True, 'max_credits': 24}
        )
        if created:
            self.stdout.write(f"Created semester: {semester.name}")

        # Departments
        cs_dept, _ = Department.objects.get_or_create(
            code='CSE',
            defaults={'name': 'Computer Science & Engineering', 'description': 'Department of Computer Science & Engineering'}
        )
        ece_dept, _ = Department.objects.get_or_create(
            code='ECE',
            defaults={'name': 'Electronics & Communication', 'description': 'Department of Electronics & Communication'}
        )
        math_dept, _ = Department.objects.get_or_create(
            code='MATH',
            defaults={'name': 'Mathematics & Basic Sciences', 'description': 'Department of Mathematics'}
        )
        se_dept, _ = Department.objects.get_or_create(
            code='SE',
            defaults={'name': 'Software Engineering & AI', 'description': 'Department of Software Engineering'}
        )

        courses_data = [
            {'code': 'CS101', 'title': 'Introduction to Computer Programming', 'department': cs_dept, 'credits': 4, 'description': 'Algorithms, problem solving, Python/C++ fundamentals, object-oriented principles.', 'fee_per_credit': 2500},
            {'code': 'CS202', 'title': 'Data Structures & Algorithms', 'department': cs_dept, 'credits': 4, 'description': 'Arrays, trees, graphs, sorting, searching, and complexity analysis.', 'fee_per_credit': 2500},
            {'code': 'CS301', 'title': 'Database Management Systems', 'department': cs_dept, 'credits': 3, 'description': 'Relational algebra, SQL, indexing, transaction processing, and MongoDB NoSQL.', 'fee_per_credit': 2500},
            {'code': 'CS305', 'title': 'Computer Networks & Security', 'department': cs_dept, 'credits': 3, 'description': 'TCP/IP architecture, socket programming, routing protocols, and network defenses.', 'fee_per_credit': 2500},
            {'code': 'CS310', 'title': 'Operating Systems Fundamentals', 'department': cs_dept, 'credits': 4, 'description': 'Process management, concurrency, virtual memory, file systems, and kernel design.', 'fee_per_credit': 2500},
            {'code': 'CS401', 'title': 'Web Engineering & Full-Stack Development', 'department': se_dept, 'credits': 4, 'description': 'Modern JS frameworks, Django backend APIs, HTML5/CSS3, and REST architecture.', 'fee_per_credit': 2500},
            {'code': 'CS405', 'title': 'Artificial Intelligence & Machine Learning', 'department': se_dept, 'credits': 4, 'description': 'Neural networks, supervised & unsupervised learning, model training with PyTorch.', 'fee_per_credit': 3000},
            {'code': 'CS412', 'title': 'Data Science & Big Data Analytics', 'department': cs_dept, 'credits': 3, 'description': 'Data mining, Pandas, Spark processing, data visualization, and predictive modeling.', 'fee_per_credit': 2800},
            {'code': 'CS420', 'title': 'Cloud Computing & DevOps Architecture', 'department': se_dept, 'credits': 3, 'description': 'AWS/GCP infrastructure, Docker containerization, Kubernetes, and CI/CD pipelines.', 'fee_per_credit': 2800},
            {'code': 'CS430', 'title': 'Cybersecurity & Ethical Hacking', 'department': cs_dept, 'credits': 3, 'description': 'Vulnerability assessment, cryptography, penetration testing, and digital forensics.', 'fee_per_credit': 3000},
            {'code': 'ECE102', 'title': 'Digital Logic & Circuit Design', 'department': ece_dept, 'credits': 3, 'description': 'Boolean algebra, logic gates, combinational and sequential circuit design.', 'fee_per_credit': 2500},
            {'code': 'ECE204', 'title': 'Microprocessors & Microcontrollers', 'department': ece_dept, 'credits': 4, 'description': 'ARM architecture, assembly programming, hardware interfacing, and timing diagrams.', 'fee_per_credit': 2500},
            {'code': 'ECE308', 'title': 'Internet of Things (IoT) & Embedded Systems', 'department': ece_dept, 'credits': 3, 'description': 'Sensor networks, ESP32/Raspberry Pi prototyping, MQTT communication protocols.', 'fee_per_credit': 2800},
            {'code': 'MATH101', 'title': 'Linear Algebra & Multivariate Calculus', 'department': math_dept, 'credits': 4, 'description': 'Matrices, vector spaces, eigenvalues, differential equations, and multivariate calculus.', 'fee_per_credit': 2500},
            {'code': 'SE201', 'title': 'Software Engineering & Agile Methodologies', 'department': se_dept, 'credits': 3, 'description': 'SDLC models, Scrum framework, software testing, QA automation, and UML modeling.', 'fee_per_credit': 2500},
        ]

        created_courses = []
        for data in courses_data:
            c, c_created = Course.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            created_courses.append(c)
            if c_created:
                self.stdout.write(f"Created course: {c.code} - {c.title}")

        # Pre-select 4 courses for student accounts by default if not enrolled yet
        default_course_codes = ['CS101', 'CS202', 'CS301', 'MATH101']
        default_courses = [c for c in created_courses if c.code in default_course_codes]

        for user in User.objects.all():
            enrollment, _ = Enrollment.objects.get_or_create(student=user, semester=semester)
            if enrollment.items.count() == 0:
                for c in default_courses:
                    EnrollmentItem.objects.get_or_create(enrollment=enrollment, course=c)
                self.stdout.write(f"Pre-selected 4 default courses for student: {user.email}")
            
            # Sync fee breakdown
            fee, _ = SemesterFee.objects.get_or_create(enrollment=enrollment)
            fee.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded 15 courses and enrolled 4 default courses for students!"))
