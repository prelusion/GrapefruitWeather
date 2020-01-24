FROM gradle:5.4.1-jdk11-slim AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src
RUN gradle build --no-daemon

FROM gradle:5.4.1-jre11-slim
WORKDIR /app
COPY --from=build /home/gradle/src/build/libs/weatherstation-1.0.jar /app/application.jar
ENTRYPOINT ["java", "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005", "-jar","/app/application.jar"]

EXPOSE 7789
EXPOSE 5005