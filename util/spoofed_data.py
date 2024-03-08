from datetime import datetime

from data.database import Article, Company, db


def insert_spoofed_data():
    """Insert spooofed data. Wrap in app.app_context()."""
    spoofed_companies = [
        {
            "name": "Acme Corp",
            "url": "http://www.acme.com",
            "description": "Leading provider of anvils and dynamite",
            "location": "Looneyville, USA",
            "market_cap": 1000000000,
            "ceo": "Wile E. Coyote",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Globex Corporation",
            "url": "http://www.globex.com",
            "description": "Global domination through innovation",
            "location": "Springfield, USA",
            "market_cap": 2000000000,
            "ceo": "Hank Scorpio",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Wonka Industries",
            "url": "http://www.wonka.com",
            "description": "Magical candy and chocolate factory",
            "location": "Fantasyland, USA",
            "market_cap": 500000000,
            "ceo": "Willy Wonka",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Stark Industries",
            "url": "http://www.stark.com",
            "description": "Cutting-edge technology and superhero gadgets",
            "location": "New York City, USA",
            "market_cap": 10000000000,
            "ceo": "Tony Stark",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Umbrella Corporation",
            "url": "http://www.umbrella.com",
            "description": "Innovative bioengineering and pharmaceuticals",
            "location": "Raccoon City, USA",
            "market_cap": 800000000,
            "ceo": "Albert Wesker",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Acme Rockets",
            "url": "http://www.acme-rockets.com",
            "description": "Specializing in explosive propulsion systems",
            "location": "Looneyville, USA",
            "market_cap": 50000000,
            "ceo": "Marvin the Martian",
            "last_scraped": datetime.now(),
        },
        {
            "name": "LexCorp",
            "url": "http://www.lexcorp.com",
            "description": "Advancing technology for a better tomorrow",
            "location": "Metropolis, USA",
            "market_cap": 3000000000,
            "ceo": "Lex Luthor",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Tyrell Corporation",
            "url": "http://www.tyrell.com",
            "description": "Creating artificial lifeforms and advanced robotics",
            "location": "Los Angeles, USA",
            "market_cap": 4000000000,
            "ceo": "Eldon Tyrell",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Wayne Enterprises",
            "url": "http://www.wayneenterprises.com",
            "description": "Building a safer Gotham through innovation",
            "location": "Gotham City, USA",
            "market_cap": 6000000000,
            "ceo": "Bruce Wayne",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Gringotts Wizarding Bank",
            "url": "http://www.gringotts.com",
            "description": "Safeguarding wizarding wealth for centuries",
            "location": "Diagon Alley, UK",
            "market_cap": 700000000,
            "ceo": "Griphook",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Spacely Sprockets",
            "url": "http://www.spacelysprockets.com",
            "description": "Premier manufacturer of sprockets for the space age",
            "location": "Orbit City, USA",
            "market_cap": 750000000,
            "ceo": "Cosmo Spacely",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Monsters, Inc.",
            "url": "http://www.monstersinc.com",
            "description": "World's top producer of screams and laughter",
            "location": "Monstropolis, USA",
            "market_cap": 850000000,
            "ceo": "James P. Sullivan",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Oceanic Airlines",
            "url": "http://www.oceanicairlines.com",
            "description": "Flying to destinations unknown",
            "location": "Los Angeles, USA",
            "market_cap": 920000000,
            "ceo": "Jacob",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Wayne Enterprises",
            "url": "http://www.wayneenterprises.com",
            "description": "Building a safer Gotham through innovation",
            "location": "Gotham City, USA",
            "market_cap": 6000000000,
            "ceo": "Bruce Wayne",
            "last_scraped": datetime.now(),
        },
        {
            "name": "Duff Beer",
            "url": "http://www.duffbeer.com",
            "description": "The beer that makes the days fly by",
            "location": "Springfield, USA",
            "market_cap": 300000000,
            "ceo": "Duffman",
            "last_scraped": datetime.now(),
        },
    ]

    for company_data in spoofed_companies:
        company = Company(
            name=company_data["name"],
            url=company_data["url"],
            description=company_data["description"],
            location=company_data["location"],
            market_cap=company_data["market_cap"],
            ceo=company_data["ceo"],
            last_scraped=company_data["last_scraped"],
        )
        db.session.add(company)

    spoofed_articles = [
        {
            "url": "https://www.bbc.co.uk",
            "headline": "Man Eats Apple",
            "publisher": "BBC",
            "date": datetime.now(),
            "summary": "Man eats an apple, says it was the best apple he'd ever eaten.",
        },
        {
            "url": "https://www.theguardian.com/uk",
            "headline": "CEO Fired After Two Hours",
            "publisher": "The Guardian",
            "date": datetime.now(),
            "summary": "CEO so terrible he was fired after just two hours on the job.",
        },
        {
            "url": "https://www.nytimes.com/",
            "headline": "New Study Finds Chocolate Consumption Linked to Increased Lifespan",
            "publisher": "New York Times",
            "date": datetime.now(),
            "summary": "A comprehensive study suggests that regular consumption of dark chocolate may lead to a longer and healthier life.",
        },
        {
            "url": "https://www.cnn.com/",
            "headline": "World's Largest Pizza Made in Italy",
            "publisher": "CNN",
            "date": datetime.now(),
            "summary": "Italy breaks the Guinness World Record for the largest pizza ever made, measuring 3 meters in diameter and weighing over 5 tons.",
        },
        {
            "url": "https://www.nationalgeographic.com/",
            "headline": "Scientists Discover New Species of Dancing Frog",
            "publisher": "National Geographic",
            "date": datetime.now(),
            "summary": "A team of biologists has discovered a new species of frog in the Amazon rainforest that performs intricate dance moves during mating rituals.",
        },
        {
            "url": "https://www.bbc.co.uk",
            "headline": "Innovative Solar-Powered Car Unveiled at Auto Show",
            "publisher": "BBC",
            "date": datetime.now(),
            "summary": "A revolutionary new car powered entirely by solar energy is showcased at an international auto show, offering a glimpse into the future of sustainable transportation.",
        },
        {
            "url": "https://www.theguardian.com/uk",
            "headline": "World's Tallest Building Completed in Dubai",
            "publisher": "The Guardian",
            "date": datetime.now(),
            "summary": "Dubai completes construction of the world's tallest building, towering over 1 kilometer high and setting a new record in architectural achievement.",
        },
        {
            "url": "https://www.nytimes.com/",
            "headline": "New Breakthrough in Cancer Treatment Offers Hope to Patients",
            "publisher": "New York Times",
            "date": datetime.now(),
            "summary": "Researchers announce a major breakthrough in cancer treatment, with a new therapy showing promising results in clinical trials and offering hope to millions of patients worldwide.",
        },
        {
            "url": "https://www.cnn.com/",
            "headline": "Ancient Artifact Discovered in Egyptian Pyramid",
            "publisher": "CNN",
            "date": datetime.now(),
            "summary": "Archaeologists uncover a rare ancient artifact buried deep within an Egyptian pyramid, shedding new light on the civilization's rich history and culture.",
        },
        {
            "url": "https://www.nationalgeographic.com/",
            "headline": "World's Largest Coral Reef Discovered in Pacific Ocean",
            "publisher": "National Geographic",
            "date": datetime.now(),
            "summary": "Marine biologists stumble upon the largest coral reef ever recorded in the Pacific Ocean, teeming with diverse marine life and offering new opportunities for scientific research and conservation efforts.",
        },
    ]
    for data in spoofed_articles:
        article = Article(
            url=data["url"],
            headline=data["headline"],
            publisher=data["publisher"],
            date=data["date"],
            summary=data["summary"],
        )
        db.session.add(article)
    db.session.commit()
