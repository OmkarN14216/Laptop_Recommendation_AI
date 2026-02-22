import asyncio
from app.database import get_database
from app.services.groq_service import groq_service
import re
import ast

async def product_map_layer(laptop):
    """Use Groq to extract ALL laptop features from specs"""
    
    delimiter = "#####"
    
    # Extract all available specs
    description = laptop.get('description', '')
    brand = laptop.get('brand', '')
    model = laptop.get('model_name', '')
    cpu = f"{laptop.get('cpu_manufacturer', '')} {laptop.get('core', '')}"
    clock = laptop.get('clock_speed', '')
    ram = laptop.get('ram_size', '')
    storage_type = laptop.get('storage_type', '')
    display_type = laptop.get('display_type', '')
    display_size = laptop.get('display_size', '')
    gpu = laptop.get('graphics_processor', '')
    resolution = laptop.get('screen_resolution', '')
    weight = laptop.get('laptop_weight', '')
    battery = laptop.get('average_battery_life', '')
    
    prompt = f"""
    You are a Laptop Specifications Classifier. Analyze the laptop specifications and classify EACH feature as 'low', 'medium', or 'high'.
    
    LAPTOP SPECS:
    Brand: {brand}
    Model: {model}
    CPU: {cpu} @ {clock}
    RAM: {ram}
    Storage: {storage_type}
    Display: {display_size} {display_type} ({resolution})
    GPU: {gpu}
    Weight: {weight}
    Battery: {battery}
    Description: {description}
    
    {delimiter}CLASSIFICATION RULES:{delimiter}
    
    1. GPU Intensity:
       - low: Integrated graphics (Intel UHD, Intel Iris, Intel HD)
       - medium: Entry/Mid dedicated (AMD Radeon, GTX 1050-1650, MX series)
       - high: High-end dedicated (NVIDIA GTX 1660+, RTX series, AMD RX series)
    
    2. Processing Speed:
       - low: i3, Ryzen 3, Celeron, Pentium, or older generations
       - medium: i5, Ryzen 5, or equivalent mid-range
       - high: i7, i9, Ryzen 7, Ryzen 9, or high-end processors
    
    3. RAM Capacity:
       - low: 4GB, 8GB
       - medium: 12GB, 16GB
       - high: 24GB, 32GB, 64GB or more
    
    4. Storage Capacity:
       - low: <512GB (128GB, 256GB, 512GB)
       - medium: 512GB-1TB
       - high: >1TB (1TB+, 2TB+)
    
    5. Storage Type:
       - low: HDD (Hard Disk Drive)
       - medium: SSD or SATA SSD
       - high: NVMe SSD, PCIe SSD, or combination HDD+SSD where SSD is primary
    
    6. Display Quality:
       - low: Resolution below Full HD (1366x768, 1280x800)
       - medium: Full HD (1920x1080), IPS/LED panels
       - high: 2K, 4K, Retina, OLED, or color-accurate displays
    
    7. Display Size:
       - low: <14 inches (11", 12", 13.3")
       - medium: 14-15.6 inches
       - high: >15.6 inches (17", 18")
    
    8. Portability (based on weight):
       - low: <1.5 kg (ultraportable, thin and light)
       - medium: 1.5-2.5 kg (standard laptops)
       - high: >2.5 kg (heavy, gaming/workstation laptops)
    
    9. Battery Life:
       - low: <6 hours
       - medium: 6-10 hours
       - high: >10 hours
    
    {delimiter}
    
    Analyze the specs above and output ONLY a Python dictionary with these EXACT 9 keys:
    
    {{'gpu intensity': 'value', 'processing speed': 'value', 'ram capacity': 'value', 'storage capacity': 'value', 'storage type': 'value', 'display quality': 'value', 'display size': 'value', 'portability': 'value', 'battery life': 'value'}}
    
    Replace 'value' with 'low', 'medium', or 'high' based on the rules above.
    Output ONLY the dictionary, no explanations.
    """
    
    response = groq_service.get_completion(prompt)
    return response.strip()

def extract_dictionary_from_string(string):
    """Extract dictionary from string"""
    regex_pattern = r"\{[^{}]+\}"
    dictionary_matches = re.findall(regex_pattern, string)
    
    if dictionary_matches:
        try:
            dictionary_string = dictionary_matches[0]
            dictionary_string = dictionary_string.lower()
            dictionary = ast.literal_eval(dictionary_string)
            return dictionary
        except Exception as e:
            print(f"Error parsing dictionary: {e}")
            return None
    return None

async def update_all_laptop_features():
    """Update features for all laptops in database using Groq analysis"""
    from app.database import connect_to_mongo
    
    await connect_to_mongo()
    db = get_database()
    
    laptops = await db.laptops.find().to_list(length=None)
    
    print(f"\n{'='*60}")
    print(f"Found {len(laptops)} laptops. Generating features using Groq AI...")
    print(f"{'='*60}\n")
    
    success_count = 0
    fail_count = 0
    
    for i, laptop in enumerate(laptops):
        print(f"[{i+1}/{len(laptops)}] Processing: {laptop['brand']} {laptop['model_name']}")
        
        try:
            # Generate features using Groq
            features_str = await product_map_layer(laptop)
            print(f"  Generated: {features_str[:100]}...")
            
            # Extract dictionary
            features_dict = extract_dictionary_from_string(features_str)
            
            if features_dict and len(features_dict) == 9:
                # Update in database
                await db.laptops.update_one(
                    {'_id': laptop['_id']},
                    {'$set': {'laptop_feature': features_dict}}
                )
                print(f"  ✅ Updated successfully")
                success_count += 1
            else:
                print(f"  ❌ Failed - Invalid dictionary (got {len(features_dict) if features_dict else 0} keys, need 9)")
                fail_count += 1
            
            # Delay to avoid rate limiting
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"Feature generation complete!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(update_all_laptop_features())