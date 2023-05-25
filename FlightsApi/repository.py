from models import models
import logging
logger = logging.getLogger()
class Repository():
    @staticmethod
    def get_by_id(model: type[models.Model], id: int):
        # TODO test existing id
        # TODO test nonexisting id
        # TODO test non-existing model
        """Get item of type model by id

        Args:
            model (type[Model]): Model to get row from
            id (int): id of the row to get

        Returns:
            Model object: An item or None if not found
        """
        return model.objects.filter(pk=id).first()
    
    @staticmethod
    def get_all(model: type[models.Model]):
        # TODO test model
        # TODO test different obj
        """Get all rows from certain model

        Args:
            model (type[Model]): The model to fetch rows from

        Returns:
            list: All rows from model
        """
        return model.objects.all()
        
    @staticmethod
    def add(new_obj):
        # TODO test missing fields
        # TODO test wrong value types
        # TODO test correct data
        """Saves a new row to a model

        Args:
            new_row (obj): A new object of the model's type
        """
        # Verify that the save method actually exists in the object
        if not hasattr(new_obj, 'save'):
            logger.error("Passed non-model object.")
        elif not callable(new_obj.save):
            logger.error("new_obj.save is not callable - is this the right object?")
        else:
            new_obj.save()
    
    @staticmethod
    def update(model: type[models.Model], id: int, **updated_values):
        # TODO test non existing fields
        # TODO test wrong value types
        # TODO test correct data
        """Update row from model with new data

        Args:
            model (type[Model]): Model to update a row in
            id (int): id of row to update
        KeywordArgs:
            Any updated values
        """
        item = Repository.get_by_id(model, id)
        for key, value in updated_values.items():
            if hasattr(item, key):
                setattr(item, key, value)
            else:
                logger.warning("Attempted to edit a non existing attribute '%s'." % key)
        item.save()
    
    @staticmethod
    def add_all(new_rows: list[type[models.Model]]):
        # TODO test bad types in list
        # TODO test good insert
        """Add all rows to database

        Args:
            new_rows (list): Model objects to add to the database
        """
        for row in new_rows:
            if not hasattr(row, 'save'):
                continue
            elif not callable(row.save):
                continue
            row.save()
    
    @staticmethod
    def remove(model, id: int):
        # TODO test nonexisting id
        # TODO test successful removal
        """Remove a row from the database

        Args:
            model (Model): the model to remove from
            id (int): The id of the row to remove
        """
        item_to_remove = Repository.get_by_id(model, id)
        if item_to_remove:
            item_to_remove.delete()
    
