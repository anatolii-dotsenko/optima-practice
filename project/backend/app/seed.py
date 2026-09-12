import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User

logger = logging.getLogger("coffee_shop.seed")


def seed_initial_data(db: Session) -> None:
    """Seeds default categories, menu items, and admin user if database is empty."""
    # Check if categories already exist
    existing_cat = db.execute(select(Category)).first()
    if existing_cat is not None:
        logger.info("Database already seeded with categories. Skipping catalog seed.")
        return

    logger.info("Seeding initial coffee shop catalog and users...")

    # 1. Categories
    coffee_cat = Category(
        name="Кава",
        slug="coffee",
        description="Свіжообсмажена спешелті кава від найкращих фермерських лотів",
        display_order=1,
        is_active=True,
    )
    tea_cat = Category(
        name="Чай та Напої",
        slug="tea",
        description="Крафтові чаї, церемоніальна матча, сезонні лимонади та какао",
        display_order=2,
        is_active=True,
    )
    bakery_cat = Category(
        name="Випічка",
        slug="bakery",
        description="Свіжоспечені французькі круасани, даніші та бріоші щоранку",
        display_order=3,
        is_active=True,
    )
    dessert_cat = Category(
        name="Десерти",
        slug="desserts",
        description="Фірмові баські чизкейки, макаруни та лимонні тарти",
        display_order=4,
        is_active=True,
    )

    db.add_all([coffee_cat, tea_cat, bakery_cat, dessert_cat])
    db.flush()

    # 2. Menu Items
    menu_items = [
        # Coffee
        MenuItem(
            category_id=coffee_cat.id,
            name="Еспресо Доппіо",
            description="Подвійна порція насиченого еспресо з нотками шоколаду",
            price=Decimal("55.00"),
            image_url="https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=coffee_cat.id,
            name="Капучино Класичний",
            description="Подвійний еспресо з шовковистою кремовою молочною пінкою, 250 мл",
            price=Decimal("70.00"),
            image_url="https://images.unsplash.com/photo-1534778101976-62847782c213?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=coffee_cat.id,
            name="Флет Вайт",
            description="Інтенсивний кавовий смак еспресо з тонким шаром мікропінки, 200 мл",
            price=Decimal("75.00"),
            image_url="https://images.unsplash.com/photo-1577968897966-3d4325b36b61?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=coffee_cat.id,
            name="Фільтр-кава дня",
            description="Світле обсмаження, приготована методом Batch Brew. Багатий букет, 300 мл",
            price=Decimal("60.00"),
            image_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500&q=80",
            is_available=True,
        ),
        # Tea & Drinks
        MenuItem(
            category_id=tea_cat.id,
            name="Матча Лате",
            description="Японська зелена матча на вівсяному або класичному молоці, 300 мл",
            price=Decimal("85.00"),
            image_url="https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=tea_cat.id,
            name="Чай Альпійський збір",
            description="Трав'яний чай з м'ятою, мелісою, ромашкою та гірським чебрецем, 400 мл",
            price=Decimal("50.00"),
            image_url="https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&q=80",
            is_available=True,
        ),
        # Bakery
        MenuItem(
            category_id=bakery_cat.id,
            name="Круасан Вершковий Класичний",
            description="Хрусткий багатошаровий круасан на фермерському французькому маслі 84%",
            price=Decimal("65.00"),
            image_url="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=bakery_cat.id,
            name="Круасан з мигдалевим кремом",
            description="Круасан, наповнений ніжним франжипаном, посипаний пелюстками мигдалю",
            price=Decimal("85.00"),
            image_url="https://images.unsplash.com/photo-1608198093002-ad4e005484ec?w=500&q=80",
            is_available=True,
        ),
        # Desserts
        MenuItem(
            category_id=dessert_cat.id,
            name="Баський чизкейк Сан-Себастьян",
            description="Карамелізована скоринка та ніжна тануча вершкова серединка з маскарпоне",
            price=Decimal("110.00"),
            image_url="https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&q=80",
            is_available=True,
        ),
        MenuItem(
            category_id=dessert_cat.id,
            name="Лимонний тарт з меренгою",
            description="Пісочна основа з освіжаючим цитрусовим курдом та обпаленою меренгою",
            price=Decimal("95.00"),
            image_url="https://images.unsplash.com/photo-1519915028121-7d3463d20b13?w=500&q=80",
            is_available=True,
        ),
    ]
    db.add_all(menu_items)

    # 3. Seed Admin User only if explicit credentials provided via environment
    if settings.FIRST_SUPERUSER_EMAIL and settings.FIRST_SUPERUSER_PASSWORD:
        existing_admin = db.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        ).scalar_one_or_none()
        if not existing_admin:
            admin_user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Адміністратор Optima",
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
            logger.info("Admin user created from environment configuration.")

    db.commit()
    logger.info("Successfully seeded catalog items.")
