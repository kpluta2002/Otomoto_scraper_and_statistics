CREATE TABLE public.price (
    id          BIGSERIAL,
    amount      FLOAT,
    currency    VARCHAR(20) NOT NULL,
    segment     VARCHAR(100),
    created_at  TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT price_pkey PRIMARY KEY (id, currency),
    CONSTRAINT fk_raw_listing FOREIGN KEY (id) REFERENCES raw_listing(id)
)
PARTITION BY LIST (currency);

CREATE TABLE price_pln PARTITION OF public.price
  FOR VALUES IN ('PLN');

CREATE TABLE price_eur PARTITION OF public.price
  FOR VALUES IN ('EUR');

CREATE INDEX ON price_pln    (segment);
CREATE INDEX ON price_eur    (segment);