import uuid
from src.models.category import Category


class CategoryRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, category_id) -> Category:
        return self.session.query(Category).filter_by(id=category_id).first()

    def get_by_name_for_user(self, user_id, name: str) -> Category:
        """Find a category by name for a specific user (case-insensitive)."""
        return self.session.query(Category).filter(
            Category.user_id == user_id,
            Category.name.ilike(name)
        ).first()

    def get_all_for_user(self, user_id) -> list[Category]:
        return self.session.query(Category).filter_by(user_id=user_id).order_by(Category.name).all()

    def get_or_create(self, user_id, name: str) -> Category:
        """Get existing category by name or create a new one."""
        category = self.get_by_name_for_user(user_id, name)
        if not category:
            category = Category(
                id=uuid.uuid4(),
                name=name.strip(),
                user_id=user_id
            )
            self.session.add(category)
            self.session.flush()
        return category

    def add(self, category: Category) -> Category:
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def read(self, category_id) -> Category:
        return self.get_by_id(category_id)

    def update(self, category: Category) -> Category:
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category_id) -> Category:
        category = self.get_by_id(category_id)
        if not category:
            return None
        self.session.delete(category)
        self.session.commit()
        return category
