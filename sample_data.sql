-- =====================================================================
-- Book Recommendation System - Sample Books
-- =====================================================================
-- Fills the books table with a starter catalogue of 116 titles.
--
-- Safe to re-run: books has UNIQUE(title, author) and every statement ends
-- with ON DUPLICATE KEY UPDATE, so running this file twice does NOT create
-- duplicate books. Users, ratings and reading lists are never touched.
-- =====================================================================

USE book_recommendation_db;

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- Classic starter set
-- ---------------------------------------------------------------------
INSERT INTO books (title, author, genre, book_description) VALUES
('The Alchemist', 'Paulo Coelho', 'Fiction', 'A shepherd boy follows his dream to find treasure, discovering the importance of following one''s Personal Legend.'),
('A Brief History of Time', 'Stephen Hawking', 'Science', 'A landmark exploration of cosmology, black holes, and the origins of the universe.'),
('The Da Vinci Code', 'Dan Brown', 'Mystery', 'A symbologist uncovers a religious conspiracy hidden in the works of Leonardo da Vinci.'),
('The God of Small Things', 'Arundhati Roy', 'Fiction', 'A novel about family, love, and tragedy in post-colonial Kerala.'),
('Cosmos', 'Carl Sagan', 'Science', 'A journey through space and time, exploring the wonders of the universe.'),
('Angels & Demons', 'Dan Brown', 'Mystery', 'Robert Langdon races to uncover a secret society''s plot against the Vatican.'),
('The Selfish Gene', 'Richard Dawkins', 'Science', 'A revolutionary look at evolution from the perspective of genes.'),
('Pride and Prejudice', 'Jane Austen', 'Fiction', 'A classic tale of love, class, and first impressions in Georgian England.'),
('Murder on the Orient Express', 'Agatha Christie', 'Mystery', 'Detective Hercule Poirot investigates a murder aboard a stranded train.'),
('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 'A powerful story about racial injustice in the American South.'),
('The Time Machine', 'H.G. Wells', 'Science', 'A Victorian scientist travels far into the future to witness the fate of humanity.'),
('The Magician''s Nephew', 'C.S. Lewis', 'Fiction', 'The prequel to the Chronicles of Narnia, telling how the magical land was created.')
ON DUPLICATE KEY UPDATE book_id = book_id;

-- ---------------------------------------------------------------------
-- Extended set
-- ---------------------------------------------------------------------
INSERT INTO books (title, author, genre, book_description) VALUES
('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 'A hobbit joins a dwarven quest to reclaim a treasure guarded by a dragon.'),
('The Lord of the Rings', 'J.R.R. Tolkien', 'Fantasy', 'An epic quest to destroy the One Ring and save Middle-earth.'),
('Harry Potter and the Philosopher''s Stone', 'J.K. Rowling', 'Fantasy', 'A young wizard discovers his magical heritage and faces a dark enemy.'),
('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy', 'Harry returns to Hogwarts to uncover a hidden chamber and a deadly mystery.'),
('1984', 'George Orwell', 'Dystopian', 'A chilling portrait of a totalitarian society ruled by surveillance and propaganda.'),
('Animal Farm', 'George Orwell', 'Dystopian', 'An allegorical tale of farm animals who overthrow their human master.'),
('The Great Gatsby', 'F. Scott Fitzgerald', 'Classics', 'A story of wealth, love, and the American Dream in the Jazz Age.'),
('Jane Eyre', 'Charlotte Bronte', 'Classics', 'An orphaned governess rises above hardship in search of love and independence.'),
('The Catcher in the Rye', 'J.D. Salinger', 'Classics', 'A disillusioned teenager wanders New York City in search of meaning.'),
('The Kite Runner', 'Khaled Hosseini', 'Fiction', 'A story of friendship, betrayal, and redemption set in Afghanistan.'),
('The Book Thief', 'Markus Zusak', 'Fiction', 'A young girl steals books and shares their power during Nazi Germany.'),
('The Fault in Our Stars', 'John Green', 'Fiction', 'Two teenagers with cancer fall in love and search for a deeper meaning.'),
('The Hunger Games', 'Suzanne Collins', 'Science Fiction', 'A dystopian arena forces tributes to fight to the death on live television.'),
('Sherlock Holmes: The Hound of the Baskervilles', 'Arthur Conan Doyle', 'Mystery', 'Holmes investigates a family curse and a deadly hound on the moors.'),
('The Silent Patient', 'Alex Michaelides', 'Thriller', 'A psychotherapist becomes obsessed with a woman who killed her husband and stopped speaking.'),
('Atomic Habits', 'James Clear', 'Self Help', 'A practical guide to building good habits and breaking bad ones.'),
('The Psychology of Money', 'Morgan Housel', 'Personal Finance', 'Timeless lessons on wealth, greed, and financial happiness.'),
('Sapiens', 'Yuval Noah Harari', 'History', 'A sweeping history of humankind from the Stone Age to the present.'),
('Wings of Fire', 'A.P.J. Abdul Kalam', 'Biography', 'The inspiring autobiography of the former President of India and missile scientist.'),
('The Lion, the Witch and the Wardrobe', 'C.S. Lewis', 'Fantasy', 'Four children step through a wardrobe into the magical land of Narnia.'),
('A Game of Thrones', 'George R.R. Martin', 'Fantasy', 'Noble houses scheme for power in a land where winter is coming.'),
('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy', 'A legendary figure recounts the story of his life and magical studies.'),
('Mistborn: The Final Empire', 'Brandon Sanderson', 'Fantasy', 'A street thief joins a rebellion against an immortal emperor.'),
('The Maze Runner', 'James Dashner', 'Science Fiction', 'Boys trapped in a giant maze fight to escape and uncover the truth.'),
('Divergent', 'Veronica Roth', 'Science Fiction', 'In a faction-based society, a girl who does not fit in must keep a secret.'),
('Ender''s Game', 'Orson Scott Card', 'Science Fiction', 'A child prodigy trains to command the fleet of Earth against an alien threat.'),
('Dune', 'Frank Herbert', 'Science Fiction', 'A desert planet holds the key to the most valuable resource in the universe.'),
('Ready Player One', 'Ernest Cline', 'Science Fiction', 'A virtual reality treasure hunt offers an ordinary boy a way out.'),
('Fahrenheit 451', 'Ray Bradbury', 'Dystopian', 'A fireman who burns books begins to question his society.'),
('Brave New World', 'Aldous Huxley', 'Dystopian', 'A futuristic society trades freedom and emotion for stability.'),
('The Picture of Dorian Gray', 'Oscar Wilde', 'Classics', 'A portrait ages while the man it shows stays forever young and corrupt.'),
('Little Women', 'Louisa May Alcott', 'Classics', 'The four March sisters grow up, face love, and pursue their dreams.'),
('Wuthering Heights', 'Emily Bronte', 'Classics', 'A passionate and tragic tale of love and revenge on the Yorkshire moors.'),
('The Old Man and the Sea', 'Ernest Hemingway', 'Classics', 'An aging fisherman battles a giant marlin on the open sea.'),
('Of Mice and Men', 'John Steinbeck', 'Classics', 'Two migrant workers dream of owning land during the Great Depression.'),
('Great Expectations', 'Charles Dickens', 'Classics', 'An orphan rises from poverty with the help of a mysterious benefactor.'),
('The Adventures of Tom Sawyer', 'Mark Twain', 'Classics', 'A mischievous boy''s adventures along the Mississippi River.'),
('The Count of Monte Cristo', 'Alexandre Dumas', 'Classics', 'A wrongly imprisoned man escapes and enacts a brilliant revenge.'),
('The Three Musketeers', 'Alexandre Dumas', 'Classics', 'A young man joins the legendary musketeers of France.'),
('And Then There Were None', 'Agatha Christie', 'Mystery', 'Ten strangers invited to an island are killed off one by one.'),
('The Murder of Roger Ackroyd', 'Agatha Christie', 'Mystery', 'Hercule Poirot investigates a village murder with a shocking twist.'),
('Gone Girl', 'Gillian Flynn', 'Thriller', 'A wife disappears and her husband becomes the prime suspect.'),
('The Girl on the Train', 'Paula Hawkins', 'Thriller', 'An alcoholic woman witnesses something disturbing on her daily commute.'),
('The Woman in the Window', 'A.J. Finn', 'Thriller', 'An agoraphobic woman spies on her neighbours and witnesses a crime.'),
('It Ends with Us', 'Colleen Hoover', 'Romance', 'A woman must confront her past when a new love enters her life.'),
('Me Before You', 'Jojo Moyes', 'Romance', 'A caregiver falls for a wheelchair-bound man who is determined to end his life.'),
('The Midnight Library', 'Matt Haig', 'Fiction', 'A woman explores alternate lives in a library between life and death.'),
('A Man Called Ove', 'Fredrik Backman', 'Fiction', 'A grumpy old man''s life is changed by his new neighbours.'),
('Tuesdays with Morrie', 'Mitch Albom', 'Biography', 'A dying professor shares his final life lessons with a former student.')
ON DUPLICATE KEY UPDATE book_id = book_id;

-- ---------------------------------------------------------------------
-- Sequels, prequels and series companions of the books above
-- ---------------------------------------------------------------------
INSERT INTO books (title, author, genre, book_description) VALUES
('The Lost Symbol', 'Dan Brown', 'Mystery', 'Robert Langdon races against time in the hidden world of Washington D.C.'),
('Inferno', 'Dan Brown', 'Mystery', 'Robert Langdon awakens in Florence with amnesia and follows a trail inspired by Dante.'),
('Origin', 'Dan Brown', 'Mystery', 'Robert Langdon hunts a discovery that threatens the foundations of religion.'),
('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 'Fantasy', 'Harry learns the truth about Sirius Black while facing the Dementors of Azkaban.'),
('Harry Potter and the Goblet of Fire', 'J.K. Rowling', 'Fantasy', 'Harry is forced into a dangerous magical tournament that hides a deadly plot.'),
('Harry Potter and the Order of the Phoenix', 'J.K. Rowling', 'Fantasy', 'Harry battles denial, prophecy, and the return of Lord Voldemort.'),
('Harry Potter and the Half-Blood Prince', 'J.K. Rowling', 'Fantasy', 'Dumbledore reveals the past of Voldemort as war returns to the wizarding world.'),
('Harry Potter and the Deathly Hallows', 'J.K. Rowling', 'Fantasy', 'Harry, Ron, and Hermione hunt the Horcruxes in the final battle against evil.'),
('Catching Fire', 'Suzanne Collins', 'Science Fiction', 'Katniss and Peeta face the Quarter Quell as rebellion begins to stir.'),
('Mockingjay', 'Suzanne Collins', 'Science Fiction', 'Katniss becomes the face of a revolution against the Capitol.'),
('The Ballad of Songbirds and Snakes', 'Suzanne Collins', 'Science Fiction', 'A young Coriolanus Snow mentors Lucy Gray Baird, a tribute from District 12.'),
('The Lightning Thief', 'Rick Riordan', 'Fantasy', 'Percy Jackson discovers he is a demigod and sets out to recover the stolen bolt of Zeus.'),
('The Sea of Monsters', 'Rick Riordan', 'Fantasy', 'Percy and his friends sail into the Sea of Monsters to save Camp Half-Blood.'),
('The Titan''s Curse', 'Rick Riordan', 'Fantasy', 'Percy must save Annabeth as the titans prepare for war.'),
('The Battle of the Labyrinth', 'Rick Riordan', 'Fantasy', 'Percy ventures into the Labyrinth to stop the titan army from invading camp.'),
('The Last Olympian', 'Rick Riordan', 'Fantasy', 'Percy leads the final defence of Olympus against Kronos and his forces.'),
('A Study in Scarlet', 'Arthur Conan Doyle', 'Mystery', 'Holmes and Watson meet for the first time and solve their first case.'),
('The Sign of the Four', 'Arthur Conan Doyle', 'Mystery', 'A treasure, a secret pact, and a murder draw Holmes into a strange case.'),
('The Valley of Fear', 'Arthur Conan Doyle', 'Mystery', 'Holmes unravels a coded murder that leads him across the Atlantic.'),
('A Clash of Kings', 'George R.R. Martin', 'Fantasy', 'Five kings war for the Iron Throne as winter approaches.'),
('A Storm of Swords', 'George R.R. Martin', 'Fantasy', 'The War of the Five Kings reaches its bloody climax.'),
('A Feast for Crows', 'George R.R. Martin', 'Fantasy', 'The aftermath of war reshapes the struggle for power in Westeros.'),
('A Dance with Dragons', 'George R.R. Martin', 'Fantasy', 'Daenerys and Jon Snow face their hardest challenges yet.'),
('The Wise Man''s Fear', 'Patrick Rothfuss', 'Fantasy', 'Kvothe continues the story of his rise to legend and his fall.'),
('The Well of Ascension', 'Brandon Sanderson', 'Fantasy', 'Vin and Elend fight to hold the empire in the wake of the Final Empire.'),
('The Hero of Ages', 'Brandon Sanderson', 'Fantasy', 'Mistborn Vin and Elend race to save the world from Ruin itself.'),
('The Scorch Trials', 'James Dashner', 'Science Fiction', 'The Gladers face a scorched wasteland and a new set of trials.'),
('The Death Cure', 'James Dashner', 'Science Fiction', 'Thomas seeks the truth about WICKED and a way to end the Maze once and for all.'),
('The Kill Order', 'James Dashner', 'Science Fiction', 'A prequel revealing the virus that sparked the Maze Runner world.'),
('Insurgent', 'Veronica Roth', 'Science Fiction', 'Tris and Four flee the factions as war erupts in Chicago.'),
('Allegiant', 'Veronica Roth', 'Science Fiction', 'Tris uncovers the truth beyond the walls of her city.'),
('Speaker for the Dead', 'Orson Scott Card', 'Science Fiction', 'Ender returns to the world he destroyed to speak for the dead.'),
('Xenocide', 'Orson Scott Card', 'Science Fiction', 'Ender and his friends try to save a race without destroying another.'),
('Children of the Mind', 'Orson Scott Card', 'Science Fiction', 'Ender finishes the battle for life across the stars.'),
('Dune Messiah', 'Frank Herbert', 'Science Fiction', 'Paul Atreides, now Emperor, faces conspiracies against his rule.'),
('Children of Dune', 'Frank Herbert', 'Science Fiction', 'The twins of Paul Atreides struggle for the future of Arrakis.'),
('God Emperor of Dune', 'Frank Herbert', 'Science Fiction', 'Leto II rules a stagnant empire and plots the escape of humanity.'),
('Little Men', 'Louisa May Alcott', 'Classics', 'Jo March runs a school where boys learn with love and patience.'),
('Jo''s Boys', 'Louisa May Alcott', 'Classics', 'The March family reunites to celebrate and send the boys into the world.'),
('Adventures of Huckleberry Finn', 'Mark Twain', 'Classics', 'Huck and Jim float down the Mississippi on a journey of friendship and freedom.'),
('Twenty Years After', 'Alexandre Dumas', 'Classics', 'The musketeers reunite during a time of civil war in France.'),
('The Vicomte de Bragelonne', 'Alexandre Dumas', 'Classics', 'The final musketeers saga, including the legend of the Man in the Iron Mask.'),
('It Starts with Us', 'Colleen Hoover', 'Romance', 'The story of Lily and Atlas continues after It Ends with Us.'),
('After You', 'Jojo Moyes', 'Romance', 'The life of Louisa Clark changes when tragedy strikes once more.'),
('Still Me', 'Jojo Moyes', 'Romance', 'Louisa Clark starts anew in New York while deciding where her heart belongs.'),
('Homo Deus: A Brief History of Tomorrow', 'Yuval Noah Harari', 'History', 'A look at where humanity is headed: gods, data, and the future of life.'),
('Go Set a Watchman', 'Harper Lee', 'Fiction', 'An adult Scout returns to Maycomb and confronts her past.'),
('A Briefer History of Time', 'Stephen Hawking', 'Science', 'A more accessible update of the classic cosmology bestseller.')
ON DUPLICATE KEY UPDATE book_id = book_id;

-- ---------------------------------------------------------------------
-- Extra titles so that every genre has at least three books.
-- (A genre with a single book can never produce a recommendation.)
-- ---------------------------------------------------------------------
INSERT INTO books (title, author, genre, book_description) VALUES
('Deep Work', 'Cal Newport', 'Self Help', 'A productivity guide about focused, distraction-free work.'),
('The 7 Habits of Highly Effective People', 'Stephen R. Covey', 'Self Help', 'Seven principles for personal and professional effectiveness.'),
('Rich Dad Poor Dad', 'Robert T. Kiyosaki', 'Personal Finance', 'A story that contrasts two very different approaches to money.'),
('The Richest Man in Babylon', 'George S. Clason', 'Personal Finance', 'Financial lessons told through parables set in ancient Babylon.'),
('Guns, Germs, and Steel', 'Jared Diamond', 'History', 'Why some societies came to dominate others, traced through geography and farming.'),
('Steve Jobs', 'Walter Isaacson', 'Biography', 'The biography of the Apple co-founder, based on hundreds of interviews.'),
('The Notebook', 'Nicholas Sparks', 'Romance', 'A love story that survives war, distance, and failing memory.')
ON DUPLICATE KEY UPDATE book_id = book_id;
