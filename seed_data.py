from flask import current_app
from models import *
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_database():
    from extensions import db
    
    # Check if data already exists
    if Zone.query.count() > 0:
        return  # Data already seeded
    
    print("Seeding database with Kebbi State data...")
    
    # Create Zones
    zones_data = [
        {'name': 'Kebbi North', 'slug': 'kebbi-north'},
        {'name': 'Kebbi Central', 'slug': 'kebbi-central'},
        {'name': 'Kebbi South', 'slug': 'kebbi-south'}
    ]
    
    zones = {}
    for zone_data in zones_data:
        zone = Zone(name=zone_data['name'], slug=zone_data['slug'])
        db.session.add(zone)
        db.session.flush()
        zones[zone_data['name']] = zone
    
    # Create LGAs with their zones
    lgas_data = {
        'Kebbi North': ['Arewa', 'Argungu', 'Augie', 'Bagudo', 'Dandi', 'Suru'],
        'Kebbi Central': ['Aliero', 'Birnin Kebbi', 'Bunza', 'Gwandu', 'Jega', 'Kalgo', 'Koko/Besse', 'Maiyama'],
        'Kebbi South': ['Danko/Wasagu', 'Fakai', 'Ngaski', 'Sakaba', 'Shanga', 'Yauri', 'Zuru']
    }
    
    lgas = {}
    for zone_name, lga_list in lgas_data.items():
        zone = zones[zone_name]
        for lga_name in lga_list:
            lga = LGA(name=lga_name, slug=lga_name.lower().replace('/', '-'), zone_id=zone.id)
            db.session.add(lga)
            db.session.flush()
            lgas[lga_name] = lga
    
    # Create Wards for each LGA
    wards_data = {
        'Aliero': ['Aliero Dangaladima I', 'Aliero Dangaladima II', 'Aliero S/Fada I', 'Aliero S/Fada II', 'Danwarai', 'Jiga Birni', 'Jiga Makera', 'Kashin Zama', 'Rafin Bauna', 'Sabiyal'],
        'Arewa': ['Bui', 'Chibike', 'Daura', 'Gorun Dikko', 'Falde', 'Feske/Jaffeji', 'Gumumdai/Rafin Tsaka', 'Kangiwa', 'Laima/Jantullu', 'Sarka/Dantsoho', 'Yeldu'],
        'Argungu': ['Gotomo', 'Dikko', 'Felande', 'Galadima', 'Gulma', 'Gwazange', 'Kokani North', 'Kokani South', 'Lailaba', 'Sauwa/Kaurar Sani', 'Tungar Zazzagawa'],
        'Augie': ['Augie North', 'Augie South', 'Bagaye/Mera', 'Bayawa North', 'Bayawa South', 'Birnin Tudu/Gudale', 'Bubuce', 'Dundaye', 'Tiggi', 'Yola'],
        'Bagudo': ['Bagudo', 'Bahindi/Boki-Doma', 'Bani/Tsamiya/Kali', 'Illo/Sabon Gari/Yantau', 'Kaoje/Gwamba', 'Kende/Kurgu', 'Lafagu/Gante', 'Lolo/Giris', 'Matsinka/Geza', 'Sharabi/Kwanguwai', 'Zagga/Kwasara'],
        'Birnin Kebbi': ['Nassarawa I', 'Nassarawa II', 'Marafa', 'Dangaladima', 'Kola/Tarasa', 'Makera', 'Maurida', 'Gwadangaji', 'Zauro', 'Gawasu', 'Kardi/Yamama', 'Lagga', 'Gulumbe', 'Ambursa', 'Ujariyo'],
        'Bunza': ['Bunza Marafa', 'Bunza Dangaladima', 'Gwade', 'Maidahini', 'Raha', 'Sabon Birni', 'Salwai', 'Tilli/Hilema', 'Tunga', 'Zogrima'],
        'Dandi': ['Bani Zumbu', 'Buma', 'Dolekaina', 'Fana', 'Maihausawa', 'Kyangakwai', 'Geza', 'Kamba', 'Kwakkwaba', 'Maigwaza', 'Shiko'],
        'Fakai': ['Bajida', 'Bangu/Garinisa', 'Birnin Tudu', 'Mahuta', 'Gulbin Kuka/Maijarhula', 'Maikende', 'Kangi', 'Fakai/Zussun', 'Marafa', 'Penin Amana/Penin Gaba'],
        'Gwandu': ['Cheberu/Bada', 'Dalijan', 'Dodoru', 'Gulmare', 'Gwandu Marafa', 'Gwandu Sarkin Fawa', 'Kambaza', 'Maruda', 'Malisa', 'Masama Kwasgara'],
        'Jega': ['Alelu/Gehuru', 'Dangamaji', 'Dunbegu/Bausara', 'Gindi/Nassarawa/Kyarmi/Galbi', 'Jandutsi/Birnin Malam', 'Jega Firchin', 'Jega Kokani', 'Jega Magaji B', 'Jega Magaji A', 'Katanga/Fagada', 'Kimba'],
        'Kalgo': ['Badariya/Magarza', 'Dangoma/Gayi', 'Diggi', 'Etene', 'Kalgo', 'Kuka', 'Mutubari', 'Nayilwa', 'Wurogauri', 'Zuguru'],
        'Koko/Besse': ['Koko Magaji', 'Illela/Sabon Gari', 'Koko Firchin', 'Dada/Alelu', 'Jadadi', 'Lani/Manyan/Tafukka/Shiba', 'Besse', 'Takware', 'Dutsin Mari/Dulmeru', 'Zariya Kalakala/Amiru', 'Madacci/Firini', 'Maikwara/Karamar Damra/Bakoshi'],
        'Maiyama': ['Andarai/Kurunkudu/Zugun Liba', 'Giwa Tazo/Zara', 'Gumbin Kure', 'Karaye/Dogondaji', 'Kawara/S/Sara/Yarkamba', 'Kuberu/Gidiga', 'Liba/Danwa/Kuka Kogo', 'Maiyama', 'Mungadi/Botoro', 'Sambawa/Mayalo', 'Sarandosa/Gubba'],
        'Ngaski': ['Birnin Yauri', 'Gafara Machupa', 'Garin Baka/Makarin', 'Kwakwaran', 'Libata/Kwangia', 'Kambuwa/Danmaraya', 'Makawa Uleira', 'Ngaski', 'Utono/Hoge', 'Wara'],
        'Sakaba': ['Adai', 'Dankolo', 'Doka/Bere', 'Gelwasa', 'Janbirni', 'Maza/Maza', 'Makuku', 'Sakaba', 'Tudun Kuka', 'Fada'],
        'Shanga': ['Atuwo', 'Binuwa/Gebbe/Bukunji', 'Dugu Tsoho/Dugu Raha', 'Kawara/Ingu/Sargo', 'Rafin Kirya/Tafki Tara', 'Sakace/Golongo/Hundeji', 'Sawashi', 'Shanga', 'Takware', 'Yarbesse'],
        'Suru': ['Aljannare', 'Bandan', 'Barbarejo', 'Bakuwa', 'Dakingari', 'Dandane', 'Daniya/Shema', 'Ginga', 'Giro', 'Kwaifa', 'Suru'],
        'Danko/Wasagu': ['Ayu', 'Bena', 'Dan Umaru/Mairairai', 'Danko/Maga', 'Kanya', 'Kyabu/Kandu', 'Ribah/Machika', 'Waje', 'Wasagu', 'Yalmo/Shindi', 'Gwanfi/Kele'],
        'Yauri': ['Chulu/Koma', 'Gungun Sarki', 'Jijima', 'Tondi', 'Yelwa Central', 'Yelwa East', 'Yelwa North', 'Yelwa South', 'Yelwa West', 'Zamare'],
        'Zuru': ['Bedi', 'Ciroman Dabai', 'Isgogo/Dago', 'Manga/Ushe', 'Rafin Zuru', 'Rikoto', 'Rumu/Daben/Seme', 'Senchi', 'Taduga', 'Zodi']
    }
    
    for lga_name, ward_list in wards_data.items():
        lga = lgas.get(lga_name)
        if lga:
            for ward_name in ward_list:
                # Create unique slug by combining LGA and ward name
                unique_slug = f"{lga_name.lower().replace('/', '-').replace(' ', '-')}-{ward_name.lower().replace('/', '-').replace(' ', '-')}"
                ward = Ward(name=ward_name, slug=unique_slug, lga_id=lga.id)
                db.session.add(ward)
    
    # Create default admin account
    admin_user = User(
        username='Kpn20',
        email='kpn2020@gmail.com',
        full_name='KPN Admin',
        role_type=RoleType.ADMIN,
        approval_status=ApprovalStatus.APPROVED,
        facebook_verified=True
    )
    admin_user.set_password('Kpn2020@1234?')
    db.session.add(admin_user)
    
    # Create ICT Admin account
    ict_admin_user = User(
        username='IctAdmin',
        email='ictadmin@kpn.org',
        full_name='ICT Administrator',
        role_type=RoleType.ICT_ADMIN,
        approval_status=ApprovalStatus.APPROVED,
        facebook_verified=True
    )
    ict_admin_user.set_password('Kpn2020@1234?')
    db.session.add(ict_admin_user)
    
    # Create default executive accounts
    executives = [
        {
            'username': 'Nasirukgw',
            'password': 'Maitonka@123',
            'full_name': 'Nasiru Saidu',
            'role_title': 'State Coordinator'
        },
        {
            'username': 'Danyola',
            'password': 'Nass001',
            'full_name': 'Nasiru Abubakar',
            'role_title': 'Director of Media & Publicity'
        },
    ]
    
    for exec_data in executives:
        exec_user = User(
            username=exec_data['username'],
            email=f"{exec_data['username'].lower()}@kpn.org",
            full_name=exec_data['full_name'],
            role_type=RoleType.EXECUTIVE,
            role_title=exec_data['role_title'],
            approval_status=ApprovalStatus.APPROVED,
            facebook_verified=True
        )
        exec_user.set_password(exec_data['password'])
        db.session.add(exec_user)
    
    # Create sample donation accounts
    donations_data = [
        {
            'bank_name': 'First Bank of Nigeria',
            'account_name': 'Kebbi Progressive Network',
            'account_number': '3085123456',
            'description': 'Main donation account for KPN activities'
        },
        {
            'bank_name': 'Zenith Bank',
            'account_name': 'KPN Welfare Fund',
            'account_number': '1014567890',
            'description': 'Special account for welfare and charity activities'
        }
    ]
    
    for donation_data in donations_data:
        donation = Donation(**donation_data)
        db.session.add(donation)
    
    db.session.commit()
    print("Database seeded successfully with Kebbi State data!")