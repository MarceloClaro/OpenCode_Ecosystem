from sqlalchemy.orm import Session
from database import SessionLocal
import models

def explore_database():
    db: Session = SessionLocal()

    print("\n📂 Clients:")
    clients = db.query(models.Client).all()
    for client in clients:
        print(f"ID: {client.id}, Name: {client.name}, Contact: {client.contact}")

    print("\n📂 Lawyers:")
    lawyers = db.query(models.Lawyer).all()
    for lawyer in lawyers:
        print(f"ID: {lawyer.id}, Name: {lawyer.name}, Specialization: {lawyer.specialization}")

    print("\n📂 Cases:")
    cases = db.query(models.Case).all()
    for case in cases:
        print(f"""
        ID: {case.id}
        Title: {case.title}
        Status: {case.status}
        Client: {case.client.name}
        Lawyer: {case.lawyer.name}
        Description: {case.description}
        Created: {case.date_created}
        """)

    db.close()

if __name__ == "__main__":
    explore_database()
