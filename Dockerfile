# Use the official Hugo image from Docker Hub
FROM klakegg/hugo:latest

# Set the working directory
WORKDIR /src

# Copy the Hugo site files into the container
COPY . /src

# Expose the port Hugo will run on
EXPOSE 1313

# Command to start Hugo server
CMD ["hugo", "server", "--bind", "0.0.0.0"]
