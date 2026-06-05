# Integração Híbrida: PennyLane + TensorFlow

A integração de circuitos quânticos com o TensorFlow permite criar modelos híbridos onde o processamento clássico e quântico são otimizados conjuntamente via backpropagation.

## Vantagens da Abordagem Híbrida
1. **Otimizadores SOTA**: Use Adam, RMSprop ou Adagrad diretamente nos parâmetros quânticos.
2. **Camadas Clássicas**: Combine Redes Neurais Convolucionais (CNNs) para extração de características com circuitos quânticos para classificação.
3. **Fluxo de Gradiente**: O PennyLane fornece interfaces nativas para que o TensorFlow trate QNodes como camadas Keras.

## Padrão de Implementação Manual
Caso as camadas de alto nível (`KerasLayer`) apresentem problemas de compatibilidade, utilize o loop de treinamento manual:

```python
import pennylane as qml
import tensorflow as tf

@qml.qnode(dev, interface="tf")
def qnode(inputs, weights):
    # Lógica do circuito
    return qml.expval(qml.PauliZ(0))

# Loop de treinamento
with tf.GradientTape() as tape:
    predictions = [qnode(x, weights) for x in X_batch]
    loss = tf.keras.losses.binary_crossentropy(y_batch, predictions)
gradients = tape.gradient(loss, [weights])
optimizer.apply_gradients(zip(gradients, [weights]))
```

## Casos de Uso
- **Classificação de Imagens Médicas**: Redução de dimensionalidade clássica seguida de classificação quântica.
- **Finanças**: Modelos de previsão de séries temporais com camadas quânticas recorrentes.
