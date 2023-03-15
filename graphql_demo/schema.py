import graphene
from .models import Product, Category
from graphene_django.types import DjangoObjectType
from .serializers import ProductSerializer, CategorySerializer
from graphene_django.rest_framework.mutation import SerializerMutation


class ProductType(DjangoObjectType):
	class Meta:
		model = Product


class CategoryType(DjangoObjectType):
	class Meta:
		model = Category


class Query(object):
	all_products = graphene.List(ProductType)
	product = graphene.Field(ProductType, id=graphene.ID())

	all_categories = graphene.List(CategoryType)
	category = graphene.Field(CategoryType, id=graphene.ID())

	def resolve_all_products(self, info, **kwargs):
		# Querying a list of products
		return Product.objects.all()

	def resolve_product(self, info, id):
		# Querying a single product
		return Product.objects.get(pk=id)

	def resolve_all_categories(self, info, **kwargs):
		# Querying a list of categories
		return Category.objects.all()

	def resolve_category(self, info, id):
		# Querying a single category
		return Category.objects.get(pk=id)


class CreateProduct(graphene.Mutation):
	# Let's define the arguments we can pass the create method
	class Arguments:
		name = graphene.String()
		price = graphene.String()
		category = graphene.List(graphene.ID)  # Yes, graphene.ID and not graphene.ID()
		in_stock = graphene.Boolean()
		date_created = graphene.types.datetime.DateTime()

	# What it returns
	product = graphene.Field(ProductType)

	# Where you really do all the mutation
	def mutate(self, _info, name, price=None, category=None, in_stock=True, date_created=None):
		print(price)
		product = Product.objects.create(
			name=name,
			price=price,
			in_stock=in_stock,
			date_created=date_created
		)

		# This is how we deal with ManyToMany
		# Loop through and add categories for our product. Simple right?
		if category is not None:
			category_set = []
			for category_id in category:
				category_object = Category.objects.get(pk=category_id)
				category_set.append(category_object)
			product.category.set(category_set)

		product.save()
		# return an instance of the Mutation
		return CreateProduct(
			product=product
		)


class UpdateProduct(graphene.Mutation):
	# The input arguments for this mutation
	class Arguments:
		id = graphene.ID()
		name = graphene.String()
		price = graphene.Float()
		category = graphene.List(graphene.ID)
		in_stock = graphene.Boolean()
		date_created = graphene.types.datetime.DateTime()

	# Let's define the response of the mutation
	product = graphene.Field(ProductType)

	def mutate(self, _info, _id, name=None, price=None, category=None, in_stock=None, date_created=None):
		product = Product.objects.get(pk=_id)
		product.name = name if name is not None else product.name
		product.price = price if price is not None else product.price
		product.in_stock = in_stock if in_stock is not None else product.in_stock
		product.date_created = date_created if date_created is not None else product.date_created

		# Loop through and update categories for our product 😫
		if category is not None:
			category_set = []
			for category_id in category:
				category_object = Category.objects.get(pk=category_id)
				category_set.append(category_object)
			product.category.set(category_set)

		product.save()
		# Notice we return an instance of this mutation 🤷‍♀️
		return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
	class Arguments:
		# The input arguments for this mutation
		id = graphene.ID()

	# The class attributes define the response of the mutation
	product = graphene.Field(ProductType)

	def mutate(self, _info, _id):
		product = Product.objects.get(pk=_id)
		if product is not None:
			product.delete()
		return DeleteProduct(product=product)


class CreateCategory(graphene.Mutation):
	class Arguments:
		# The input arguments for this mutation
		name = graphene.String()

	category = graphene.Field(CategoryType)

	def mutate(self, _info, name):
		category = Category.objects.create(
			name=name
		)
		# We've done this so many times, it no longer feels weird
		return CreateCategory(
			category=category
		)


class UpdateCategory(graphene.Mutation):
	class Arguments:
		# The input arguments for this mutation
		id = graphene.ID()
		name = graphene.String()

	# The class attributes define the response of the mutation
	category = graphene.Field(CategoryType)

	def mutate(self, info, id, name):
		category = Category.objects.get(pk=id)
		category.name = name if name is not None else category.name
		category.save()
		# Notice we return an instance of this mutation
		return UpdateCategory(category=category)


class DeleteCategory(graphene.Mutation):
	class Arguments:
		# The input arguments for this mutation
		id = graphene.ID()

	# The class attributes define the response of the mutation
	category = graphene.Field(CategoryType)

	def mutate(self, info, id):
		category = Category.objects.get(pk=id)
		if category is not None:
			# Notice we don't do category.delete()? That's because we must not
			category.delete()
		# Notice we return an instance of this mutation
		return DeleteCategory(category=category)


class CreateProductMutation(SerializerMutation):
	class Meta:
		serializer_class = ProductSerializer
		model_operations = ['create', 'update']
		lookup_field = 'id'


class Mutation(graphene.ObjectType):
	create_product = CreateProductMutation.Field()
	update_product = UpdateProduct.Field()
	delete_product = DeleteProduct.Field()

	create_category = CreateCategory.Field()
	update_category = UpdateCategory.Field()
	delete_category = DeleteCategory.Field()
