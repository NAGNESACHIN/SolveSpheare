INSERT INTO products (name, brand, category, description, source)
VALUES ('ReviewIQ Demo Phone', 'DemoBrand', 'Smartphone', 'Demo product for local development', 'seed')
ON CONFLICT DO NOTHING;
