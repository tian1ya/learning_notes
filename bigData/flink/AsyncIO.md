Ship、sold to code lob sales_group shiptoname

12726180
12761242
12785546





                    UPDATE raw.t_dim_ship_to_oem
                    SET end_time=start_time, is_valid=0 
                    WHERE ship_to_code=N'12726180' AND is_valid=1 AND is_active=1;
                
            INSERT INTO raw.t_dim_ship_to_oem
            SELECT ['oem_ship_to_id', 'ship_to_code', 'sold_to_code', 'sales_group', 'account_group', 'lob', 'ship_to_name', 'city_code', 'address', 'post_code', 'transpzone', 'contact_person', 'contact_person_email_address', 'contact_person_telephone', 'contact_person_fax', 'contact_person_mobile', 'terms_of_payment', 'order_block', 'banding', 'gka', 'start_time', 'end_time'], 1 AS is_valid, 0 AS is_active
            FROM raw.t_dim_ship_to_oem
            WHERE ship_to_code=N'12726180' AND is_valid=1 AND is_active=1;