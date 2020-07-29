package se.kth.castor.extractClassUsage;

import spoon.MavenLauncher;
import spoon.OutputType;
import spoon.processing.AbstractProcessor;
import spoon.reflect.declaration.CtType;
import spoon.reflect.reference.CtArrayTypeReference;
import spoon.reflect.reference.CtTypeReference;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class Main {
    public static void main(String[] args) {
        MavenLauncher launcher = new MavenLauncher(args[0], MavenLauncher.SOURCE_TYPE.APP_SOURCE);
        launcher.getEnvironment().setOutputType(OutputType.NO_OUTPUT);
        final Set output = new HashSet<String>();
        launcher.addProcessor(new AbstractProcessor<CtTypeReference>() {
            @Override
            public void process(CtTypeReference element) {
                try {
                    if (element instanceof CtArrayTypeReference) {
                        element = ((CtArrayTypeReference) element).getComponentType();
                    }
                } catch (Exception e) {
                    // ignore
                }
                try {
                    CtType declaration = element.getDeclaration();
                    if (declaration != null) {
                        if (declaration.isGenerics()) {
                            return;
                        }
                    }
                } catch (Exception e) {
                    // ignore
                }
                try {
                    String name = element.getQualifiedName();
                    output.add(name);
                } catch (Exception e) {
                    // ignore
                }
            }
        });
        launcher.run();

        for (Iterator iterator = output.iterator(); iterator.hasNext(); ) {
            String next = (String) iterator.next();
            System.out.println(next);
        }
    }
}
