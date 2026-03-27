-- ==============================
-- Tabela: user
-- ==============================
BEGIN;
INSERT INTO harmonia."user" (user_fullname, user_email, user_profile, user_password_hash) VALUES
('Beto Beginner', 'beto.beginner1@email.com', 1, 'b1d0e95f0b06d2502a49bb2c8861966247bdaeb5d1a1e7eae36fafcdf770b8c9'),
('Ive Intermediate', 'ive.intermediate1@email.com', 2, '7f45e762c0a64c884b32cf159b637c245cbbaff6cffde75d9357271e5ed20c42'),
('Alex Advanced', 'alex.advanced1@email.com', 3, 'e7ca2dbf5326b6a7898cd9c69f7d3a60914e12c3be9e8eb0fbda71609b303a1c'),
('Elena Expert', 'elena.expert1@email.com', 4, '22fa5b8fd33e146c149fbbb0a71539926f2f8c9bdad93a3fdc8ffa42f0baa15b');
COMMIT;
