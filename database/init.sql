CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS cheese_inventory (
  id SERIAL PRIMARY KEY,
  cheese_type TEXT,
  quantity INT,
  location TEXT,
  quality TEXT
);

CREATE TABLE IF NOT EXISTS admin_notes (
  id SERIAL PRIMARY KEY,
  title TEXT,
  content TEXT,
  author TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Seed Users
INSERT INTO users (username, password, role) VALUES
('admin','super_secret_admin_pass_2025!','admin'),
('jerry','cheeselover','user'),
('tom','meowmeow123','user'),
('spike','guarddog','user');

-- Seed Inventory
INSERT INTO cheese_inventory (cheese_type, quantity, location, quality) VALUES
('Cheddar', 10, 'Vault A', 'A'),
('Brie', 7, 'Vault B', 'B+'),
('Gouda', 5, 'Vault A', 'A-'),
('Swiss', 9, 'Vault C', 'B'),
('Blue', 4, 'Vault D', 'C+'),
('Parmesan', 12, 'Vault A', 'A'),
('Mozzarella', 8, 'Vault B', 'B');

-- Seed Admin Note with Flag
INSERT INTO admin_notes (title, content, author)
VALUES
('Master Key Location',
 'The master key to Jerry''s cage is hidden behind the portrait in the living room. Flag: Exploit3rs{sql_i_2025_v1}',
 'admin');
