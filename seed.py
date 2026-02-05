"""
Seed script to populate database with sample data

Run this script to add initial data to your database:
    python seed.py
"""

from app import app
from database import db
from models import Author, Book, Category


def seed_database():
    """Seed the database with sample data"""
    
    with app.app_context():
        # Clear existing data (optional - remove if you want to keep existing data)
        print("Clearing existing data...")
        db.session.query(Book).delete()
        db.session.query(Author).delete()
        db.session.query(Category).delete()
        db.session.commit()
        
        print("Creating categories...")
        # Create categories
        fiction = Category(
            name="Fiction",
            description="Literary works based on imagination"
        )
        programming = Category(
            name="Programming",
            description="Books about software development"
        )
        science = Category(
            name="Science",
            description="Scientific literature and research"
        )
        history = Category(
            name="History",
            description="Historical accounts and analysis"
        )
        business = Category(
            name="Business",
            description="Business and entrepreneurship"
        )
        
        db.session.add_all([fiction, programming, science, history, business])
        db.session.commit()
        
        print("Creating authors...")
        # Create authors
        robert_martin = Author(
            name="Robert C. Martin",
            bio="Software engineer and author, known for promoting software design principles",
            country="USA"
        )
        
        martin_fowler = Author(
            name="Martin Fowler",
            bio="British software developer, author and international speaker",
            country="UK"
        )
        
        eric_evans = Author(
            name="Eric Evans",
            bio="Software developer and author who coined the term Domain-Driven Design",
            country="USA"
        )
        
        george_orwell = Author(
            name="George Orwell",
            bio="English novelist and essayist, journalist and critic",
            country="UK"
        )
        
        yuval_harari = Author(
            name="Yuval Noah Harari",
            bio="Israeli public intellectual, historian and professor",
            country="Israel"
        )
        
        db.session.add_all([robert_martin, martin_fowler, eric_evans, george_orwell, yuval_harari])
        db.session.commit()
        
        print("Creating books...")
        # Create books
        
        # Programming books
        clean_code = Book(
            title="Clean Code: A Handbook of Agile Software Craftsmanship",
            isbn="9780132350884",
            year=2008,
            author_id=robert_martin.id,
            description="Even bad code can function. But if code isn't clean, it can bring a development organization to its knees.",
            pages=464
        )
        clean_code.categories.extend([programming])
        
        clean_architecture = Book(
            title="Clean Architecture",
            isbn="9780134494166",
            year=2017,
            author_id=robert_martin.id,
            description="Building upon the success of best-sellers Clean Code and The Clean Coder, renowned software craftsman Robert C. Martin shows how to bring greater professionalism and discipline to application architecture.",
            pages=432
        )
        clean_architecture.categories.extend([programming, business])
        
        refactoring = Book(
            title="Refactoring: Improving the Design of Existing Code",
            isbn="9780201485677",
            year=1999,
            author_id=martin_fowler.id,
            description="As the application of object technology--particularly the Java programming language--has become commonplace, a new problem has emerged to confront the software development community.",
            pages=464
        )
        refactoring.categories.extend([programming])
        
        ddd = Book(
            title="Domain-Driven Design: Tackling Complexity in the Heart of Software",
            isbn="9780321125217",
            year=2003,
            author_id=eric_evans.id,
            description="Eric Evans has written a fantastic book on how you can make the design of your software match your mental model of the problem domain you are addressing.",
            pages=560
        )
        ddd.categories.extend([programming, business])
        
        # Fiction books
        nineteen_eighty_four = Book(
            title="1984",
            isbn="9780451524935",
            year=1949,
            author_id=george_orwell.id,
            description="A dystopian social science fiction novel and cautionary tale about the dangers of totalitarianism.",
            pages=328
        )
        nineteen_eighty_four.categories.extend([fiction, history])
        
        animal_farm = Book(
            title="Animal Farm",
            isbn="9780451526342",
            year=1945,
            author_id=george_orwell.id,
            description="A satirical allegorical novella reflecting events leading up to the Russian Revolution and the Stalinist era.",
            pages=112
        )
        animal_farm.categories.extend([fiction, history])
        
        # History/Science books
        sapiens = Book(
            title="Sapiens: A Brief History of Humankind",
            isbn="9780062316097",
            year=2011,
            author_id=yuval_harari.id,
            description="Explores the history of humankind from the Stone Age to the twenty-first century.",
            pages=443
        )
        sapiens.categories.extend([history, science])
        
        homo_deus = Book(
            title="Homo Deus: A Brief History of Tomorrow",
            isbn="9780062464316",
            year=2015,
            author_id=yuval_harari.id,
            description="Explores the projects, dreams and nightmares that will shape the twenty-first century.",
            pages=450
        )
        homo_deus.categories.extend([history, science])
        
        db.session.add_all([
            clean_code, clean_architecture, refactoring, ddd,
            nineteen_eighty_four, animal_farm,
            sapiens, homo_deus
        ])
        db.session.commit()
        
        print("\n" + "="*70)
        print("✅ Database seeded successfully!")
        print("="*70)
        print(f"📚 Created {Category.query.count()} categories")
        print(f"✍️  Created {Author.query.count()} authors")
        print(f"📖 Created {Book.query.count()} books")
        print("="*70 + "\n")
        
        # Print sample data
        print("Sample Authors:")
        for author in Author.query.all():
            print(f"  • {author.name} ({author.country}) - {author.books.count()} books")
        
        print("\nSample Categories:")
        for category in Category.query.all():
            print(f"  • {category.name} - {len(category.books)} books")
        
        print("\nSample Books:")
        for book in Book.query.limit(5).all():
            print(f"  • {book.title} by {book.author.name} ({book.year})")


if __name__ == '__main__':
    print("\n🌱 Seeding database with sample data...\n")
    seed_database()
