CREATE TABLE IF NOT EXISTS owner_schedule_blocks (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL,
    day_of_week INT NOT NULL, -- 0 = Monday ... 6 = Sunday
    block_start TIME NOT NULL,
    block_end TIME NOT NULL
);
