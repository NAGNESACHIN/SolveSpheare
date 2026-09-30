INSERT INTO products (id, name, brand, category, description, source)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'ReviewIQ Demo Phone',
  'DemoBrand',
  'Smartphone',
  'Demo product for Product Review Intelligence and Voice of Customer analytics.',
  'seed'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO reviews (product_id, external_review_id, title, review_text, rating, verified_purchase, source, language)
VALUES
('00000000-0000-0000-0000-000000000001','demo-001','Excellent battery','Battery life is excellent and the performance is smooth. Camera quality is great too.',5,true,'seed','en'),
('00000000-0000-0000-0000-000000000001','demo-002','Good display','The display is bright and the screen looks amazing, but the battery charging is slow.',4,true,'seed','en'),
('00000000-0000-0000-0000-000000000001','demo-003','Performance issues','Performance is good, but the app crashes sometimes and the software update was confusing.',3,true,'seed','en'),
('00000000-0000-0000-0000-000000000001','demo-004','Poor delivery','The phone quality is good but delivery was late and the package arrived damaged.',3,false,'seed','en'),
('00000000-0000-0000-0000-000000000001','demo-005','Not worth the price','The camera is disappointing and the price is expensive. Customer service was not helpful.',2,false,'seed','en'),
('00000000-0000-0000-0000-000000000001','demo-006','Great value','Excellent phone for the price. The design is comfortable and the performance is fast.',5,true,'seed','en')
ON CONFLICT (source, external_review_id) DO NOTHING;
