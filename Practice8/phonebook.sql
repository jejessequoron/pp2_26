DROP TABLE IF EXISTS phb;

CREATE TABLE phb (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    surname VARCHAR(100),
    phone VARCHAR(30)
);

CREATE OR REPLACE FUNCTION search_pat(pattern TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    surname VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.surname, p.phone
    FROM phb p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.surname ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%'
    ORDER BY p.id;
END;
$$ LANGUAGE plpgsql;






CREATE OR REPLACE PROCEDURE ins_upd_user(
    p_name VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM phb
        WHERE name = p_name AND surname = p_surname
    ) THEN
        UPDATE phb
        SET phone = p_phone
        WHERE name = p_name AND surname = p_surname;
    ELSE
        INSERT INTO phb(name, surname, phone)
        VALUES (p_name, p_surname, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;







CREATE OR REPLACE PROCEDURE ins_many_users(
    p_names VARCHAR[],
    p_surnames VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    bad_data TEXT := '';
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_surnames, 1)
       OR array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'All arrays must have the same length';
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9]{11,12}$' THEN
            IF EXISTS (
                SELECT 1
                FROM phb
                WHERE name = p_names[i] AND surname = p_surnames[i]
            ) THEN
                UPDATE phb
                SET phone = p_phones[i]
                WHERE name = p_names[i] AND surname = p_surnames[i];
            ELSE
                INSERT INTO phb(name, surname, phone)
                VALUES (p_names[i], p_surnames[i], p_phones[i]);
            END IF;
        ELSE
            bad_data := bad_data ||
                        '(' || p_names[i] || ', ' || p_surnames[i] || ', ' || p_phones[i] || ')' || E'\n';
        END IF;
    END LOOP;

    RAISE NOTICE 'Incorrect data:%', E'\n' || bad_data;
END;
$$;





CREATE OR REPLACE FUNCTION gpp(p_lim INT, p_ofs INT)
RETURNS TABLE (
    id INT,
    name VARCHAR,
    surname VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT phb.id, phb.name, phb.surname, phb.phone
    FROM phb
    ORDER BY phb.id
    LIMIT p_lim
    OFFSET p_ofs;
END;
$$ LANGUAGE plpgsql;






CREATE OR REPLACE PROCEDURE del_user(p_value VARCHAR)
AS $$
BEGIN
    DELETE FROM phb
    WHERE name = p_value
       OR surname = p_value
       OR phone = p_value;
END;
$$ LANGUAGE plpgsql;