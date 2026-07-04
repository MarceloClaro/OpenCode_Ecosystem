"""
Adaptadores — Ponte entre entrypoints legados e a CLI canônica.

Cada adaptador encapsula a lógica de invocação de um subsistema existente,
permitindo que a CLI canônica `ecosystem` delegue para qualquer módulo
sem acoplamento direto.
"""
