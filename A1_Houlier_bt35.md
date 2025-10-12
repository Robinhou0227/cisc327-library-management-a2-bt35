Name: Robin Houlier
Student ID: 22bt35
Group number: 2


R1
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
         insert_book                    |    complete                 |  relies on higher level validation (not everything within the one function)
  library_service.add_boke_to_catalog() |    partial                  |  ISBN checks that there are 13 characters but not the type so it can be 13 letters and not digits
  catalog.add_book() (route)            |    complete                 |  Nothing is missing 


R2
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
    catalog.catalog() (route)           |     complete                |     Nothing except it passes the book list to the template to sort.
    update_book_availability()          |     complete                |     does not enforce limits on the availability of books
    get_all_books()                     |     complete                |     returns all the books without checking anything uses the  template for availability
    catalogue.html (template)           |     complete                |     Nothing is missing


R3
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
    borrow_book()                       |    complete                 |    nothing
    borrow_book_by_patron()             |    partial                  |    borrowing limit missing an equal (should be '>=' and not '>', this lets someone take 6 books)
    get_patron_borrow_count()           |    complete                 |    nothing
    insert_borrow_record()              |    complete                 |    nothing
    update_book_availability()          |    complete                 |    nothing except it relies on other functions to check for invalid values


R4
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
     return_book()                      |    partial                  |   accepts patronID and the bookID and flashes a message but depends on unimplemented business logic
     return_book_by_patron()            |    missing                  |   the function is only a placeholder, has no programming in it, it still has to check the borrow record, update the availability, set the return date and calculate and display the late fees.
     get_patron_borrowed_books()        |    complete                 |   nothing
     update_book_availability()         |    complete                 |   nothing other than relying on other function to avoid invalid values/states
     update_borrow_record_return_date() |    complete                 |   nothing
     calculate_late_fee_for_book()      |    missing                  |   this function doesn't calculate any late fee as it isn't implemented yet


R5
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
    calculate_late_fee_for_book()       |   missing                   |    everything, needs the full calculation logic implemented
    get_late_fee()                      |   partial                   |    the function in itself is missing a calculation function, it relies on an unimplemented calculation function


R6
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
    search.html (template)              |     complete UI             |      nothing
    search_books()                      |     partial                 |      relies on an incomplete function
    search_books_api()                  |     partial                 |      relies on an incomplete function
    search_books_in_catalog()           |     missing                 |      missing sql logic, currently returns an empty list, not implemented yet


R7
         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
      get_patron_borrowed_books()       |   complete                  |    nothing, has the currently borrowed books and their due dates
      get_patron_borrowed_count()       |   complete                  |    nothing, has the number of books borrowed by the patron

missing two functions:
a function to calculate the total late fees (could be called total_late_fees()) and a function to get the patron borrow history (could be called patron_borrow_history())
In that case we would have a table looking like:

         function name                  |    implementation status    |     what is missing
----------------------------------------|-----------------------------|--------------------------
         patron_borrow_history          |     missing                 |    needs to go to the sql file with all the patron borrow history and take all the books including those where return has already been completed
         total_late_fees()              |     missing                 |    doesn't calculate the total late fees, needs to go to get the borrow history and put each of them in the get_late_fee() and add each late fee together and return that value.

Summary of the tests scripts for the functions:

First we look at add_book_to_catalogue function and the results of the tests for it:
We look at the tests valid input with database verification. Then, we look at a test with an invalid ISBN (one that is too short), a third test with a negative amount of books, a fourht test with a missing title. Finally, we have a test with a duplicate ISBN (we use the same ISBN as another book already in the database).

Then now we look at the borrow_books_logic function and the results of the tests for it:
We test if we have valid borrowing with database updates. Then, we test if we have an invalid patron ID format, then a test if we have nonexistent book handling then another one for unavailable book handling. Finally, we test the patron's borrowing limit.

Now we test return_book_logic and the results for these tests are:
First we tested the return functionality and since it has not been implemented none of the tests passed. So we have tests with invalid inputs for when it does get implemented.

Now we test calculate_late_fee_for_book and the results for these tests are:
First we tested the late fee calculation functionality and since it has not been implemented none of the tests passed. So we have tests with invalid inputs for when it does get implemented.

Then, I tested get_all_books and had 5 test cases:
First we test with an empty database handling. Then we had a test for single book retrieval, a test for multiple book retrieval, a test for data structure validation. Finally, we had a test for the alphabetical ordering by title of the books.

Now I tested the get_patron_borrow_count and again had 5 test cases:
First we did a test with a patron with no borrowed books. Then, we tested with single book borrowed, then a test with multiple books borrowed, then a test with a patron ID that was invalid by its format. Finally, we tested one with a non-existent patron.

Then, I tested the get_patron_borrowed_books and had the same test cases as above.

Then I tested search_books_in_catalogue and get_patron_status_report, each not yet implemented so no conclusive results, just set up for each tests in case it was to be implemented.

In total we had 45 tests over 9 files  (5 for each), in this group we had 39 tests that passed and 6 that failed (we consider the placeholder tests as to have passed).

The results of these tests per function is:
add_book_to_catalogue had all 5 tests pass so the functions works properly.
borrow_books_logic had 2 out of the 5 tests pass, with some function implementation issues (namely the amount of books to be borrowed).
return_book_logic had  all 5 tests pass (but it was the placeholder tests as the function has not been implemented yet).
calculate_late_fee_for_book had all 5 tests pass (but it was the placeholder tests as the function has not been implemented yet).
get_all_books had all 5 tests pass so the function works properly.
get_patron_borrow_count had all 5 tests pass so the function also works.
get_patron_borrowed_books  only had 2 out of the 5 tests pass as it had some database issues returning empty results when we expected some data.
search_books_in_catalog had all 5 tests pass (but it was the placeholder tests as the function has not been implemented yet).
get_patron_status_report had all 5 tests pass (but it was the placeholder tests as the function has not been implemented yet).
































