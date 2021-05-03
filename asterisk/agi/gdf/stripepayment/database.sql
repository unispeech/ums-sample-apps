CREATE TABLE IF NOT EXISTS gdf_stripe_transactions (
   id                    INTEGER(11)         NOT NULL AUTO_INCREMENT                   COMMENT 'unique identifier of gdf transactions',
   caller_id             VARCHAR(256)            NULL                                  COMMENT 'caller_id retreived from Asterisk',
   call_id               VARCHAR(256)            NULL                                  COMMENT 'unique call_id retreived from Asterisk',
   result                VARCHAR(256)        NOT NULL                                  COMMENT 'result status from stripe transaction ',
   transaction_id        VARCHAR(256)            NULL                                  COMMENT 'stripe transaction id ',
   transaction_date      TIMESTAMP           NOT NULL DEFAULT        CURRENT_TIMESTAMP 
                                                 ON UPDATE           CURRENT_TIMESTAMP COMMENT 'timestamp of last record creation in gdf_stripe_transactions',
   PRIMARY KEY (id)
) CHARACTER SET utf8 COMMENT 'gdf app stripe transactions .';  
 