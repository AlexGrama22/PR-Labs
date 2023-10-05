import re
import json
import socket

class Homework:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_products(self):
        products = []
        products_page = self.get_page_content('/product')
        if products_page:
            product_links = re.findall(r'href="(/product/\d+)"', products_page)
            for link in product_links:
                product_details = self.get_page_content(link)
                if product_details:
                    product_details = self.parse_product_page(product_details)  
                    if product_details:
                        product_id = int(link.strip('/product/'))
                        product_details['id'] = product_id
                        products.append(product_details)

        return products

    def get_page_content(self, path):
        """Get the content of a specific page from the web server."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            request = f'GET {path} HTTP/1.1\r\nHost: {self.host}\r\n\r\n'
            s.sendall(request.encode())
            response = s.recv(4096).decode()

        print(f"Raw Response for {path}:")
        print(response)

        if '\n\n' not in response:
            print(f"Unexpected response format for {path}. No delimiter found.")
            return None

        header, content = response.split('\n\n', 1)
        content = content.strip() if content else 'Empty content'

        return content

    def parse_product_page(self, content):
        pattern = re.compile(
            r'<h1>(?P<name>.*?)</h1>.*?'
            r'<p>Factory: (?P<factory>.*?)</p>.*?'
            r'<p>Price: \$(?P<price>[\d.]+)</p>.*?'
            r'<p>(?P<description>.*?)</p>',
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(content)
        if match:
            product_details = match.groupdict()
            product_details['price'] = float(product_details['price'])
            return product_details
        return None

    def get_simple_page_content(self, path):
        page_content = self.get_page_content(path)
        if page_content:
            filename = path.strip('/').replace('/', '_') + '.html'
            if not filename.strip():
                filename = 'index.html'
            with open(filename, 'w') as file:
                file.write(page_content)
            print(f"Content of {path} saved to {filename}")
        else:
            print(f"Failed to retrieve content for {path}")


if __name__ == "__main__":
    homework = Homework("127.0.0.1", 4000)


    products = homework.get_products()
    print(json.dumps(products, indent=4))
    with open('output.json', 'w') as f:
        json.dump(products, f, indent=4)
    print("Products saved to output.json")


    for path in ['/', '/about', '/cart']:
        homework.get_simple_page_content(path)
