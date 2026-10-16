-- 插入作者
INSERT INTO front_author(name,age,email) VALUES
('曹雪芹',35,'cxq@qq.com'),
('吴承恩',28,'wce@qq.com'),
('罗贯中',36,'lgz@qq.com'),
('施耐庵',46,'sna@qq.com');

-- 插入出版社
INSERT INTO front_publisher(name) VALUES
('中国邮电出版社'),
('清华大学出版社');

-- 插入图书
INSERT INTO front_book(name,pages,price,rating,author_id,publisher_id) VALUES
('三国演义',987,98,4.8,3,1),
('水浒传',967,97,4.83,4,1),
('西游记',1004,95,4.85,2,2),
('红楼梦',1007,99,4.9,1,2);

-- 插入订单
INSERT INTO front_book_order(book_id,price) VALUES
(1,95),
(1,85),
(1,88),
(2,94),
(2,93);
