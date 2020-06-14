from .AwsProvider import AwsProvider
from .AzureProvider import AzureProvider
from .DigitalOceanProvider import DigitalOceanProvider
from .GoogleCloudProvider import GoogleCloudProvider

all_providers = {
    'aws': AwsProvider,
    'azure': AzureProvider,
    'digitalocean': DigitalOceanProvider,
    'googlecloud': GoogleCloudProvider,
}

def provider_factory(configuration):
    type = configuration['type']
    credentials = configuration['credentials']
    for provider_type, provider_class in all_providers.items():
        if provider_type == type:
            return provider_class(credentials)

    raise KeyError('No provider found for type ' + type)
