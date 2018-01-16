# Development information

## Open questions

* How does selecting a folder node and updating the window title work?
* How does renaming a folder node work?

Ideas:
* Create two parts in the application:
  1. One part where only *notes* (i.e. content nodes) are considered.
     This is the part that talks to DAO, storage, synchronization
  2. One part where *content nodes* and *folder nodes* are considered.
     This is the part that talks to the controller, the views.
  * I don't want to create two different views.

* Work with notes (i.e. content nodes) as the primary concept.
  Make the controller create additional events to support the application with working with folders.

  Command | Aggregate | Events
  --- | --- | ---
  CreateNote | Note | NoteCreated
  RenameNote | Note | NoteRenamed
  SetNotePayload | Note | NotePayloadChanged
  OpenNote | | NoteOpened
  DeleteNote | Note | NoteDeleted
  DeleteFolder | Note* + Controller | NoteDeleted* + FolderDeleted
  RenameFolder | Note* + Controller | NoteRenamed* + FolderDeleted
  OpenFolder | Controller | FolderOpened
  
  The controller is a process manager of sorts.

* As the previous alternative, but with services and a repository:

  * NoteRepository to load and store notes
  * NoteService to work with notes
    * Listens for Commands
    * Loads the Aggregate
    * Executes Command
    * Saves Aggregate in Repository
    * Publishes generated events
  * FolderService to work with folders
    * Listens for Commands
    * Uses the NoteService to delete notes, for example, by publishing Commands on the bus
    * Publishes its own events

Lees https://lostechies.com/gabrielschenker/2015/06/06/event-sourcing-applied-the-aggregate/