**Apache Arrow In spark**

> `Arrow` is an in-memory columnar(柱状) data format in spark to efficiently transfer  data between `JVM` and Python processesm, this currently is most beneficail to `Python` users that work with `Pandas/Numpy` data, Its usage is  not automatic and might require some minor changes to configuration or code to take full advantage and ensure cpmpatibility.

**Ensure PyArrow Installed**

> `pyArrow is automatically bought in when install  `PySpark` use `pip`

**Enabling for Conversion to/from pandas**

>`Arrow` is avilable as an optimization when converting a Spark DataFrame to a pandas DataFrame  using the call `toPandas()`
>
>To use this sparl need configure with `spark.sql.execution.arrow.enabled` to `true`
>
>This is disabled by default.

```python
import numpy as np
import pandas as pd

spark.conf.set('spark.sql.execution.arrow.enabled', 'true')

pdf = pd.DataFrame(np.random.rand(100, 3))

df = spark.createDataFrame(pdf)

# Using the above optimizations with Arrow will 
# produce the same results as when Arrow is not enabled
# enabled is for optimization
result_pdf = df.select("*").toPandas()
```

#### Pandas UDFs
Arrow to transfer data and Pandas to work with the data. 
A Pandas UDF is defined using the keyword pandas_udf as a 
decorator or to wrap the function, no additional 
configuration is required

* **Scalar**

    >  used for vectorizing scalar operations They can be used with functions such as select and withColumn，Spark will execute a Pandas UDF by splitting columns into batches and calling the function for each batch as a subset of the data, then concatenating the results together.

