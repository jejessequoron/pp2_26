CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact does not exist';
    END IF;

    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name)
    DO UPDATE SET name = EXCLUDED.name
    RETURNING id INTO v_group_id;

    UPDATE contacts
    SET group_id = v_group_id
    WHERE name = p_contact_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact does not exist';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INTEGER,
    name VARCHAR,
    surname VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.surname,
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(string_agg(p.type || ': ' || p.phone, ', ' ORDER BY p.id), '') AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name ILIKE '%' || p_query || '%'
       OR c.surname ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR EXISTS (
            SELECT 1
            FROM phones p2
            WHERE p2.contact_id = c.id
              AND p2.phone ILIKE '%' || p_query || '%'
       )
    GROUP BY c.id, g.name
    ORDER BY c.id;
END;
$$;