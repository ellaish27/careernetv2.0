# seed_universities.py
from app import create_app
from extensions import db
from models import University

def seed_universities():
    app = create_app()
    with app.app_context():
        # Check if data already exists to prevent duplicates
        if University.query.first():
            print("⚠️ Universities already exist in the database. Skipping seed.")
            return

        universities_data = [
            # --- PUBLIC UNIVERSITIES ---
            {"name": "Makerere University", "website": "https://www.mak.ac.ug", "uni_type": "Public"},
            {"name": "Kyambogo University", "website": "https://kyu.ac.ug", "uni_type": "Public"},
            {"name": "Mbarara University of Science and Technology (MUST)", "website": "https://must.ac.ug", "uni_type": "Public"},
            {"name": "Gulu University", "website": "https://gu.ac.ug", "uni_type": "Public"},
            {"name": "Busitema University", "website": "https://busitema.ac.ug", "uni_type": "Public"},
            {"name": "Soroti University", "website": "https://soroti.ac.ug", "uni_type": "Public"},
            {"name": "Muni University", "website": "https://muni.ac.ug", "uni_type": "Public"},
            {"name": "Kabale University", "website": "https://kabale.ac.ug", "uni_type": "Public"},
            {"name": "Fountain University", "website": "https://fountain.ac.ug", "uni_type": "Public"}, # Note: Often classified as Private but Govt-supported, keeping as Public per common student perception or change to Private if strict
            {"name": "Uganda Christian University (UCU)", "website": "https://ucu.ac.ug", "uni_type": "Private"}, # Moved to Private
            
            # --- PRIVATE UNIVERSITIES ---
            {"name": "Uganda Christian University (UCU)", "website": "https://ucu.ac.ug", "uni_type": "Private"},
            {"name": "Kampala International University (KIU)", "website": "https://kiu.ac.ug", "uni_type": "Private"},
            {"name": "Nkumba University", "website": "https://nkumbauniversity.ac.ug", "uni_type": "Private"},
            {"name": "Bugema University", "website": "https://bugemauniv.ac.ug", "uni_type": "Private"},
            {"name": "Uganda Martyrs University (UMU)", "website": "https://umu.ac.ug", "uni_type": "Private"},
            {"name": "Islamic University in Uganda (IUIU)", "website": "https://iuiu.ac.ug", "uni_type": "Private"},
            {"name": "St. Lawrence University", "website": "https://slau.ac.ug", "uni_type": "Private"},
            {"name": "Ndejje University", "website": "https://ndejjeuniversity.ac.ug", "uni_type": "Private"},
            {"name": "Victoria University", "website": "https://vu.ac.ug", "uni_type": "Private"},
            {"name": "Cavendish University Uganda", "website": "https://cavendish.ac.ug", "uni_type": "Private"},
            {"name": "Team University", "website": "https://team.ac.ug", "uni_type": "Private"},
            {"name": "International Health Sciences University (IHSU)", "website": "https://ihsu.ac.ug", "uni_type": "Private"},
            {"name": "Kampala University", "website": "https://kamu.ac.ug", "uni_type": "Private"},
            {"name": "Metropolitan International University", "website": "https://miu.ac.ug", "uni_type": "Private"},
            {"name": "Aga Khan University", "website": "https://aku.edu", "uni_type": "Private"},
            {"name": "Lubaga Hospital Institute of Health Sciences", "website": "https://lubagahospital.org", "uni_type": "Private"},
            {"name": "Uganda Pentecostal University", "website": "https://upu.ac.ug", "uni_type": "Private"},
            {"name": "Bishop Stuart University", "website": "https://bsu.ac.ug", "uni_type": "Private"},
            {"name": "All Saints University Lango", "website": "https://asul.ac.ug", "uni_type": "Private"},
            {"name": "Busoga University", "website": "https://busogauniversity.ac.ug", "uni_type": "Private"}
        ]

        for uni_data in universities_data:
            # Check if specific university already exists to avoid errors on re-run
            if not University.query.filter_by(name=uni_data['name']).first():
                new_uni = University(
                    name=uni_data['name'],
                    website=uni_data['website'],
                    uni_type=uni_data['uni_type']
                )
                db.session.add(new_uni)
        
        try:
            db.session.commit()
            print(f"✅ Successfully seeded {len(universities_data)} universities into the database.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding database: {e}")

if __name__ == '__main__':
    seed_universities()