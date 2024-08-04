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
    sender VARCHAR(255) NOT NULL, 
    date_received DATETIME NOT NULL,
    bodytext TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS correspondents (
    id int AUTO_INCREMENT PRIMARY KEY,
    email_name VARCHAR(255),
    email_address VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS email_correspondents (
    email_id int,
    correspondent_id int,
    mention ENUM('TO', 'CC', 'BCC') NOT NULL,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
    FOREIGN KEY (correspondent_id) REFERENCES correspondents(id) ON DELETE CASCADE,
    PRIMARY KEY (email_id, correspondent_id, mention)
);
