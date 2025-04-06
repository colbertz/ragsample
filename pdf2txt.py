import PyPDF2
import sys

def pdf_to_txt(pdf_path, txt_path):
    """
    从PDF提取所有文本并保存到TXT文件
    :param pdf_path: PDF文件路径
    :param txt_path: 输出的TXT文件路径
    """
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
        
        print(f"成功提取文本到 {txt_path}")
    
    except Exception as e:
        print(f"处理PDF时出错: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python splittxt.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    txt_path = input_file.replace('.pdf', '.txt')
    pdf_to_txt(input_file, txt_path)

if __name__ == "__main__":
    main()