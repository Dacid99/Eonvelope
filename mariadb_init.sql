CREATE DATABASE IF NOT EXISTS email_archive;

USE email_archive;


CREATE TABLE IF NOT EXISTS accounts (
    id int AUTO_INCREMENT PRIMARY KEY,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    email_password VARCHAR(255) NOT NULL,
    email_server VARCHAR(255) NOT NULL,
    email_server_port int,
    email_protocol ENUM('IMAP', 'POP', 'EXCHANGE') NOT NULL
);

CREATE TABLE IF NOT EXISTS mailboxes (
    id int AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    account_id int,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS emails (
    id int AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL, 
    account_id int,
    date_received DATETIME NOT NULL,
    bodytext TEXT NOT NULL
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS correspondents (
    id int AUTO_INCREMENT PRIMARY KEY,
    email_name VARCHAR(255),
    email_address VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS email_correspondents (
    email_id int,
    correspondent_id int,
    mention ENUM('FROM', 'TO', 'CC', 'BCC') NOT NULL,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
    FOREIGN KEY (correspondent_id) REFERENCES correspondents(id) ON DELETE CASCADE,
    PRIMARY KEY (email_id, correspondent_id, mention)
);



DELIMITER //

CREATE PROCEDURE safe_insert_email(IN new_message_id VARCHAR(255), IN new_sender VARCHAR(255), IN new_date_received DATETIME, IN new_bodytext TEXT)
BEGIN
    IF NOT EXISTS (SELECT 1 FROM emails WHERE message_id = new_message_id) THEN
        INSERT INTO emails (message_id, sender, date_received, bodytext) VALUES (new_message_id, new_sender, new_date_received, new_bodytext);
    END IF;
END //

CREATE PROCEDURE safe_insert_correspondent(IN new_email_name VARCHAR(255), IN new_email_address VARCHAR(255))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM correspondents WHERE email_address = new_email_address) THEN
       INSERT INTO correspondents (email_name, email_address) VALUES (new_email_name, new_email_address);
    END IF;
END //

CREATE PROCEDURE safe_insert_email_correspondent(IN new_email_message_id VARCHAR(255), IN new_correspondent_id int, IN new_mention ENUM('FROM','TO', 'CC', 'BCC'))
BEGIN
    DECLARE new_email_id int;

    SELECT id INTO new_email_id FROM emails WHERE message_id = new_email_message_id LIMIT 1;

    IF new_email_id IS NOT NULL THEN 
        IF NOT EXISTS (SELECT 1 FROM email_correspondents WHERE email_id = new_email_id AND correspondent_id = new_correspondent_id) THEN
            INSERT INTO email_correspondents (email_id, correspondent_id, mention) VALUES (new_email_id, new_correspondent_id, new_mention);
        END IF;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ID not found';
    END IF;
END //

DELIMITER ;
