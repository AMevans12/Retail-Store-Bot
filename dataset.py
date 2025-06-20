""" This script will generate a fake dataset that will be later on used for the bot to process in the bot.py script. If you 
already have a dataset then don't execute it. """


import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
random.seed(42)


categories = {
    "Gaming Console": ["Sony", "Microsoft", "Nintendo"],
    "PC Components": ["Intel", "AMD", "NVIDIA", "Corsair"],
    "Laptops": ["Dell", "HP", "ASUS", "Lenovo", "Apple"],
    "Monitors": ["LG", "Samsung", "BenQ", "Acer"],
    "Headphones": ["Sony", "Bose", "Sennheiser", "SteelSeries"],
    "Accessories": ["Logitech", "Razer", "HyperX", "Corsair"],
    "Video Games": ["Call of Duty", "FIFA", "Cyberpunk 2077", "Elden Ring", "GTA V"]
}


num_products = 250
product_data = []

for _ in range(num_products):
    category = random.choice(list(categories.keys()))
    brand_or_game = random.choice(categories[category])
    product_name = fake.word().capitalize() + (" " + brand_or_game if category != "Video Games" else "")
    
    product_data.append({
        "Category": category,
        "Brand/Game": brand_or_game,
        "Product_Name": product_name,
        "Price": round(np.random.uniform(20, 3000), 2),
        "Stock_Availability": np.random.choice(["In Stock", "Out of Stock", "Limited Stock"], p=[0.7, 0.2, 0.1]),
        "Ratings": round(np.random.uniform(1, 5), 1),
        "Number_of_Reviews": np.random.randint(5, 5000),
        "Discount_%": np.random.randint(0, 50)
    })


df = pd.DataFrame(product_data)


df["Final_Price"] = (df["Price"] * (1 - df["Discount_%"] / 100)).round(2)


dataset_path = "gaming_products_data.csv"
df.to_csv(dataset_path, index=False)

print(f"Dataset saved successfully at {dataset_path}")
print(df.head())
