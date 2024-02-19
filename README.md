
# Typeahead


[Demo](https://github.com/andrew-candela/typeahead/assets/20376875/3ba66172-19c4-41bc-8b5b-744c23f26f58)


You know when you type something into Google and google
corects your spelling mistake? How hard would it be to
make something like this on your own? Turns out it's
not as easy as I thought.

I've got something that kind of works, but it took a while
and it doesn't work as well as I'd like.

## The good

- Missing characters are sometimes handled well
- It seems sufficiently fast
- it allows for on-the-fly updates.

With the addition of a cacheing layer I think this would
be a B+ typeahead system.

## The bad

- Typos of certain kinds are not handled well
    - Inserting extra characters completely breaks the correction algorithm
    - Accidentally typing a correct word will prevent correction
- I compute all suggestions and then trim the results to a certain number.
I should stop when I get to the required amount.
- The cache doesn't exist yet
