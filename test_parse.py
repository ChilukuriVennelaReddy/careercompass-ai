import json

buffer = ""
aiFullText = ""

chunks = [
    b'data: {"text": "Ni"}\n\n',
    b'data: {"text": "elsen"}\n\n',
    b'data: {"text": " Norman"}\n\n',
    b'data: {"text": " Group"}\n\n',
    b'data: {"text": " (NN/g)"}\n\n',
    b'data: [DONE]\n\n'
]

for value in chunks:
    buffer += value.decode('utf-8')
    lines = buffer.split('\n')
    buffer = lines.pop()
    
    for line in lines:
        if line.startswith('data: '):
            data = line[6:].strip()
            if data == '[DONE]':
                break
            try:
                parsed = json.loads(data)
                if 'text' in parsed:
                    aiFullText += parsed['text']
            except Exception as e:
                print(f"Failed to parse: {data}")

print("Result:", aiFullText)
