import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from models import Publisher, Book, Shop, Stock, Sale, create_tables
import json
import os

def fill_test_data(session):
    file_path = os.path.join(os.getcwd(), 'tests_data.json')
    
    with open(file_path, encoding='utf-8') as f:
        json_data = json.load(f)

        for string in json_data:
            model = {
                'publisher': Publisher,
                'shop': Shop,
                'book': Book,
                'stock': Stock,
                'sale': Sale,
            }[string.get('model')]

            session.add(model(id=string.get('pk'), **string.get('fields')))

        session.commit()

def main():
    login = 'postgres'
    password = ''
    db_address = 'localhost:5432'
    db_name = 'books_db'

    DSN = f'postgresql://{login}:{password}@{db_address}/{db_name}'

    engine = sq.create_engine(DSN)
    create_tables(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    fill_test_data(session)

    result = {
        'book_title': [],
        'shop_name': [],
        'price': [],
        'date': []
    }

    for book_title in session.query(Book).join(Publisher.book).filter(
                                    Publisher.name.like(input())).all():
        for sale_info in session.query(Sale).join(Stock.sale).join(Stock.book).filter(
                                    Book.title.like(f'{book_title}')).all():
            sale_info_arr = f'{sale_info}'.split(", ")
            shop_name = session.query(Shop).join(Stock.shop).join(Stock.sale).filter(
                                    Sale.id == int(sale_info_arr[0])).all()[0]
            
            result['book_title'].append(f'{book_title}')
            result['shop_name'].append(f'{shop_name}')
            result['price'].append(sale_info_arr[1])
            result['date'].append(sale_info_arr[2].split(" ")[0])
    
    session.close()
    
    max_len_book = (max(map(len, result['book_title'])))
    max_len_shop = (max(map(len, result['shop_name'])))
    max_len_price = (max(map(len, result['price'])))
    max_len_date = (max(map(len, result['date'])))
    
    output = list(zip(result['book_title'], 
                      result['shop_name'],
                      result['price'],
                      result['date']))
    
    print()
    
    for data_string in output:
        print(data_string[0].ljust(max_len_book) + ' | ' + 
              data_string[1].ljust(max_len_shop) + ' | ' +
              data_string[2].ljust(max_len_price) + ' | ' +
              data_string[3].ljust(max_len_date))

if __name__ == '__main__':
    main()