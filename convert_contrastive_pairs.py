"""
Convert contrastive pairs JSON to CSV format for RAG system
"""
import json
import csv
import sys

def convert_contrastive_pairs(json_path, csv_path):
    """
    Convert JSON contrastive pairs to CSV format
    
    Input JSON format:
    {
      "contrastive_pairs": [
        {
          "prompt": "...",
          "love_response": "...",
          "hate_response": "..."
        }
      ]
    }
    
    Output CSV format:
    text1,text2,label
    "love_response","hate_response",0.0
    """
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pairs = data.get('contrastive_pairs', [])
    
    # Create CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text1', 'text2', 'label'])
        
        for pair in pairs:
            prompt = pair.get('prompt', '')
            love_response = pair.get('love_response', '')
            hate_response = pair.get('hate_response', '')
            
            if love_response and hate_response:
                # Love vs Hate are contrasting (dissimilar) - label 0.0
                writer.writerow([love_response, hate_response, 0.0])
                
                # Optionally: Add context with prompt
                # Format: "Prompt: ... Answer: ..."
                love_with_context = f"{prompt} {love_response}"
                hate_with_context = f"{prompt} {hate_response}"
                writer.writerow([love_with_context, hate_with_context, 0.0])
    
    print(f"✅ Converted {len(pairs)} pairs to {csv_path}")
    print(f"📊 Total rows: {len(pairs) * 2} (with context variations)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        input_path = "/Users/podpeople/Downloads/contrastive_pairs_dataset.json"
    else:
        input_path = sys.argv[1]
    
    output_path = "data/contrastive_pairs.csv"
    
    print(f"📂 Reading from: {input_path}")
    convert_contrastive_pairs(input_path, output_path)
    print(f"\n🎯 Contrastive pairs ready for training!")
    print(f"   Location: {output_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Start Docker: docker-compose up -d")
    print(f"   2. Train model: curl -X POST http://localhost:8000/train-contrastive")
    print(f"   3. Index articles: curl -X POST http://localhost:8000/index-articles")
