from crypto_utils.report_signer import verificar_firma_reporte

print("Firma profesor válida:", verificar_firma_reporte(1, 3, "profesor"))
print("Firma director válida:", verificar_firma_reporte(1, 4, "director"))