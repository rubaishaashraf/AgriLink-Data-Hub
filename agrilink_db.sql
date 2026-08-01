CREATE DATABASE IF NOT EXISTS agrilink_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE agrilink_db;

-- Farmers
CREATE TABLE farmers (
    farmer_id      INT AUTO_INCREMENT PRIMARY KEY,
    first_name     VARCHAR(80)  NOT NULL,
    last_name      VARCHAR(80)  NOT NULL,
    email          VARCHAR(120) UNIQUE,
    phone          VARCHAR(20),
    farm_name      VARCHAR(120) NOT NULL,
    location       VARCHAR(150) NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crop catalog
CREATE TABLE crops (
    crop_id        INT AUTO_INCREMENT PRIMARY KEY,
    crop_name      VARCHAR(100) NOT NULL UNIQUE,
    category       ENUM('Grain','Vegetable','Fruit','Legume','Root','Other') NOT NULL,
    description    TEXT
);

-- Seasons
CREATE TABLE seasons (
    season_id      INT AUTO_INCREMENT PRIMARY KEY,
    season_name    VARCHAR(80) NOT NULL,
    year           YEAR NOT NULL,
    start_date     DATE NOT NULL,
    end_date       DATE NOT NULL,
    UNIQUE KEY uq_season (season_name, year)
);

-- Production records (farmer + crop + season)
CREATE TABLE production_records (
    record_id      INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id      INT NOT NULL,
    crop_id        INT NOT NULL,
    season_id      INT NOT NULL,
    planting_date  DATE NOT NULL,
    harvest_date   DATE NULL,
    area_hectares  DECIMAL(8,2) NOT NULL CHECK (area_hectares > 0),
    yield_kg       DECIMAL(12,2) DEFAULT 0,
    status         ENUM('Planted','Growing','Harvested') DEFAULT 'Planted',
    notes          TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prod_farmer FOREIGN KEY (farmer_id) REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    CONSTRAINT fk_prod_crop   FOREIGN KEY (crop_id)   REFERENCES crops(crop_id)   ON DELETE RESTRICT,
    CONSTRAINT fk_prod_season FOREIGN KEY (season_id) REFERENCES seasons(season_id) ON DELETE RESTRICT
);

-- Fertilizer catalog
CREATE TABLE fertilizers (
    fertilizer_id  INT AUTO_INCREMENT PRIMARY KEY,
    fertilizer_name VARCHAR(120) NOT NULL UNIQUE,
    fertilizer_type ENUM('Organic','Chemical','Mixed') NOT NULL,
    unit           ENUM('kg','L','bag') NOT NULL DEFAULT 'kg',
    npk_ratio      VARCHAR(20)
);

-- Inventory (one row per fertilizer type)
CREATE TABLE fertilizer_inventory (
    inventory_id   INT AUTO_INCREMENT PRIMARY KEY,
    fertilizer_id  INT NOT NULL UNIQUE,
    quantity       DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level  DECIMAL(10,2) NOT NULL DEFAULT 10,
    last_updated   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_inv_fert FOREIGN KEY (fertilizer_id) REFERENCES fertilizers(fertilizer_id) ON DELETE CASCADE
);

-- Fertilizer applications linked to production records
CREATE TABLE fertilizer_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    record_id      INT NOT NULL,
    fertilizer_id  INT NOT NULL,
    application_date DATE NOT NULL,
    quantity_used  DECIMAL(10,2) NOT NULL CHECK (quantity_used > 0),
    notes          TEXT,
    CONSTRAINT fk_app_record FOREIGN KEY (record_id) REFERENCES production_records(record_id) ON DELETE CASCADE,
    CONSTRAINT fk_app_fert   FOREIGN KEY (fertilizer_id) REFERENCES fertilizers(fertilizer_id) ON DELETE RESTRICT
);

-- Sample data
INSERT INTO farmers (first_name, last_name, email, phone, farm_name, location) VALUES
('Maria', 'Santos', 'maria@farm.com', '09171234567', 'Green Valley Farm', 'Laguna'),
('Juan', 'Reyes', 'juan@farm.com', '09179876543', 'Sunrise Acres', 'Nueva Ecija');

INSERT INTO crops (crop_name, category, description) VALUES
('Rice', 'Grain', 'Staple crop'),
('Corn', 'Grain', 'Feed and food crop'),
('Tomato', 'Vegetable', 'High-value vegetable');

INSERT INTO seasons (season_name, year, start_date, end_date) VALUES
('Wet Season', 2025, '2025-06-01', '2025-11-30'),
('Dry Season', 2026, '2026-01-01', '2026-05-31');

INSERT INTO fertilizers (fertilizer_name, fertilizer_type, unit, npk_ratio) VALUES
('Urea', 'Chemical', 'kg', '46-0-0'),
('Compost', 'Organic', 'kg', '2-1-1'),
('Complete Fertilizer', 'Mixed', 'bag', '14-14-14');

INSERT INTO fertilizer_inventory (fertilizer_id, quantity, reorder_level) VALUES
(1, 500.00, 50.00),
(2, 200.00, 30.00),
(3, 80.00, 20.00);

INSERT INTO production_records (farmer_id, crop_id, season_id, planting_date, area_hectares, status) VALUES
(1, 1, 1, '2025-06-15', 2.50, 'Growing'),
(2, 2, 1, '2025-07-01', 1.75, 'Planted');