from pypdf import PdfReader

def recursive_split(text, max_size=1000, overlap=200, separators=None):
    if separators is None:
        separators = ["\n\n", "\n", " ", ""]
    
    if len(text) <= max_size:
        return [text]
        
    for sep in separators:
        if sep == "":
            break
        if sep in text:
            parts = text.split(sep)
            chunks = []
            current_chunk = []
            current_len = 0
            
            for part in parts:
                part_len = len(part) + (len(sep) if current_chunk else 0)
                if current_len + part_len <= max_size:
                    current_chunk.append(part)
                    current_len += part_len
                else:
                    if current_chunk:
                        chunks.append(sep.join(current_chunk))
                    
                    # Backtrack to implement overlap
                    overlap_chunk = []
                    overlap_len = 0
                    for p in reversed(current_chunk):
                        p_len = len(p) + (len(sep) if overlap_chunk else 0)
                        if overlap_len + p_len <= overlap:
                            overlap_chunk.insert(0, p)
                            overlap_len += p_len
                        else:
                            break
                    current_chunk = overlap_chunk + [part]
                    current_len = sum(len(p) for p in current_chunk) + len(sep) * (len(current_chunk) - 1)
            
            if current_chunk:
                chunks.append(sep.join(current_chunk))
            return chunks

    # Sliding window fallback
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start+max_size])
        start += (max_size - overlap)
    return chunks

class PDFIngestionService:
    @staticmethod
    def extract_and_split_pdf(file_stream):
        reader = PdfReader(file_stream)
        chunks = []
        
        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            text = page.extract_text()
            if not text:
                continue
            
            text = text.strip()
            if not text:
                continue
                
            page_chunks = recursive_split(text, max_size=1000, overlap=200)
            for chunk_text in page_chunks:
                chunk_text = chunk_text.strip()
                if chunk_text:
                    chunks.append({
                        'content': chunk_text,
                        'page_number': page_num
                    })
                    
        return chunks
